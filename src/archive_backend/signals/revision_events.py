from django.db import IntegrityError
from archive_backend.jobs.util import pkStringList
from archive_backend.models import Edition, Revision, RevisionStatus
from archive_backend.generation import make_new_generated_revision_filters
from django_q.tasks import async_task

def PostNewRevisionEvent(instance: Revision):
    """Fired upon a new revision being created, to handle things such as automatic generation and creating new revision for dependencies."""
    if instance.status == RevisionStatus.REQUESTABLE:
        if (instance.belongs_to.generation_config.automatically_regenerate 
            or instance.remote_peer.mirror_files):
            RequestRevision(instance)
    for dependency in instance.belongs_to.generation_dependencies.all(): #generational dependencies are by definition always local editions
        CreateLocalRequestableRevision(dependency)

def DoesItemNeedNewRevision(sender: Revision, edition_to_generate: Edition):
    return (make_new_generated_revision_filters
            .get(edition_to_generate.generation_config.make_new_generated_revision_filter)
            (edition_to_generate, sender, edition_to_generate.generation_config))

def CreateLocalRequestableRevision(self : Edition):
    """Creates a new local requestable revision for an edition, if needed. Used to symbolize revisions that can be generated."""
    #Unfinished is filted for the case where a previously regular version with 
    # an unfinished revision is changed to a generated version
    latestRevision = self.revisions.order_by('-date').exclude(status=RevisionStatus.UNFINISHED).first()

    #Automatic generation is handled by the revision signal logic itself
    if latestRevision is None:
        rev = Revision.objects.create(belongs_to = self, status = RevisionStatus.REQUESTABLE)
        rev.save()
        return rev
    if latestRevision.status == RevisionStatus.ONDISKPUBLISHED:
        rev = Revision.objects.create(belongs_to = self, status = RevisionStatus.REQUESTABLE)
        rev.save()
        return rev
    if latestRevision.status == RevisionStatus.REQUESTABLE:
        #somehow the revision is requestable and a call for another one is given, 
        # call new revision event on it to be sure it gets back into the pipeline
        PostNewRevisionEvent(latestRevision)
        return latestRevision
    if latestRevision.status == RevisionStatus.REMOTEJOBSCHEDULED or latestRevision.status == RevisionStatus.REMOTEREQUESTABLE:
        raise IntegrityError("Revision requested to be generated has remote job or remote requestable revisions, should not be possible. Revision ID: " + str(latestRevision.pk))
    #revision is already scheduled
    return latestRevision
    
def _requestGeneratedRevision(self: Revision):
    """Requests a revision to be generated.
    
    If the parent revision is not ONDISKPUBLISHED, it will recursively 
    request the parent revisions.
    
    Edition it belongs to must be a valid generation configuration."""
    latestParentRevision = (self.belongs_to
                            .actively_generated_from
                            .revisions.exclude(status = RevisionStatus.UNFINISHED)
                            .order_by('-date')
                            .first())
    if latestParentRevision is None:
        raise IntegrityError("""Parent edition has no revisions, should not be possible, 
                             even remote editions should have an empty requestable revision 
                             for generation purposes. If this edition is manually created
                             a new, ensure code makes an initial empty ondisk revision for code integrity. Edition ID: """ 
                             + str(self.belongs_to.actively_generated_from.pk))
    if latestParentRevision.status == RevisionStatus.ONDISKPUBLISHED:
        _queueGenerationJobForRevision(self)
    else:
        RequestRevision(latestParentRevision)

def _queueGenerationJobForRevision(self: Revision):
    """Queues a revision job for generation."""
    if self.status != RevisionStatus.JOBSCHEDULED:
        raise IntegrityError("Revision is not in a state to be queued for generation. Revision ID: " + str(self.pk))
    async_task('archive_backend.jobs.generate_revisions', pkStringList([self]),
               task_name=("Generating revision for edition: " + self.belongs_to.title)[:100])

def _downloadRemoteRevision(self: Revision):
    """Downloads a remote revision."""
    if self.status != RevisionStatus.JOBSCHEDULED or self.status != RevisionStatus.REQUESTABLE:
        raise IntegrityError("Revision is not in a state to be downloaded. Revision ID: " + str(self.pk))
    async_task('archive_backend.jobs.download_latest_revision_for_editions', pkStringList([self.belongs_to]),
               task_name=("Downloading latest revision for edition: " + self.belongs_to.title)[:100])
    
def _requestRemoteRequestable(self: Revision):
    """Requests a remote job."""
    if self.status != RevisionStatus.REMOTEJOBSCHEDULED:
        raise IntegrityError("Revision is not in a state to be queued for remote request. Revision ID: " + str(self.pk))
    async_task('archive_backend.jobs.request_remote_requestable', str(self.pk),
               task_name=("Requesting remote requestable for edition: " + self.belongs_to.title)[:100])

def RequestRevision(self: Revision):
    match self.status:
        case RevisionStatus.ONDISKPUBLISHED:
            return #No need to request, it is already on disk
        case RevisionStatus.JOBSCHEDULED:
            return #No need to request, it is already scheduled for generation
        case RevisionStatus.UNFINISHED:
            raise ValueError("Unfinished revision is requested. Illegal operation, can only call request for generation to OnDisk, JobScheduled or Requestable revisions. Revision ID: " + str(Revision.pk))
        case RevisionStatus.REQUESTABLE:
            self.status = RevisionStatus.JOBSCHEDULED
            self.save()

            if self.belongs_to.from_remote.is_this_site:
                _requestGeneratedRevision(self) #Generate the revision
            else:
                _downloadRemoteRevision(self) #Download the revision

        case RevisionStatus.REMOTEREQUESTABLE:
            self.status = RevisionStatus.REMOTEJOBSCHEDULED
            self.save()
            _requestRemoteRequestable(self)

        case RevisionStatus.REMOTEJOBSCHEDULED:
            _requestRemoteRequestable(self)



