from django.db import IntegrityError
from archive_backend.jobs.util import pkStringList
from archive_backend.models import Edition, Revision, RevisionStatus
from archive_backend.generation import make_new_generated_revision_filters
from django_q.tasks import async_task

def PostNewRevisionEvent(instance: Revision):
    """Fired upon a new revision being created, to handle things such as automatic generation and creating new revision for dependencies."""
    if instance.status == RevisionStatus.REQUESTABLE:
        if instance.belongs_to.generation_config is not None:
            #Generated local revision
            if instance.belongs_to.generation_config.automatically_regenerate:
                RequestRevision(instance)#Generate the revision
        else:
            if instance.from_remote.mirror_files:
                RequestRevision(instance)#Download the files

    for dependency in instance.belongs_to.generation_dependencies.all(): #generational dependencies are by definition always local editions
        CreateLocalRequestableRevision(dependency, instance)

def DoesItemNeedNewRevision(generate_from: Revision, edition_to_generate: Edition):
    return (make_new_generated_revision_filters
            .get(edition_to_generate.generation_config.make_new_generated_revision_filter)
            (edition_to_generate, generate_from, edition_to_generate.generation_config))

def CreateLocalGeneratedRequestableRevisionFromEdition(edition: Edition):
    """Creates a new local requestable revision for an edition. 
    
    Uses the latest revision of the parent edition as a base at time of calling.
    
    Skips check for if it needs to make a new revision."""
    makefrom = edition.actively_generated_from.revisions.exclude(status = RevisionStatus.UNFINISHED).order_by("-date").first()
    if makefrom is None:
        raise IntegrityError("Parent edition has no revisions, should not be possible, even remote editions should have an empty requestable revision")
    CreateLocalRequestableRevision(edition, makefrom)

def CreateLocalRequestableRevision(for_edition: Edition, from_revision: Revision):
    """Creates a new local requestable revision for an edition, if needed. Used to symbolize revisions that can be generated or downloaded from a remote."""
    i = Revision.objects.create(belongs_to = for_edition, status = RevisionStatus.REQUESTABLE, generated_from = from_revision).save()
    return i
    
def _requestGeneratedRevision(self: Revision):
    """Requests a revision to be generated.
    
    If the parent revision is not ONDISKPUBLISHED, it will recursively 
    request the parent revisions.
    
    Edition it belongs to must be a valid generation configuration."""
    if self.generated_from is None:
        raise IntegrityError("""Revision requested for generation has no "generated_from" value, should not be possible.
                             Edition ID: """ 
                             + str(self.belongs_to.actively_generated_from.pk))
    if self.generated_from.status == RevisionStatus.ONDISKPUBLISHED:
        _queueGenerationJobForRevision(self)
    else:
        RequestRevision(self.generated_from)

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
    """Requests a revision to be generated or downloaded. Recursively calls parent revisions for download/generation if needed."""
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



