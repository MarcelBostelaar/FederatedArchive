from django.db import IntegrityError
from archive_backend.jobs.util import pkStringList
from archive_backend.models import Edition, existanceType, Revision
from archive_backend.models.revision_file_models import RevisionStatus
from django_q.tasks import async_task

def validate_generation_config(self: Edition):
    """Validates that the edition is of type GENERATED and has a generation config and a parent edition"""
    if self.existance_type != existanceType.GENERATED:
        raise ValueError("Edition is not of type GENERATED. Edition ID: " + str(self.pk))
    if self.generation_config is None or self.actively_generated_from is None:
        raise IntegrityError("Edition doesnt have a config for generation or a parent edition. Edition ID: " + str(self.pk))

def CreateGeneratedRevision(self : Edition):
    """Creates a new revision for the generated edition, and schedules it for generation.
    
    Edition must be of type GENERATED and have a generation config."""
    validate_generation_config(self)
    newRev = Revision(
        belongs_to = self, 
        status = RevisionStatus.REQUESTABLE)
    newRev.save()
    if Edition.generation_config.automatically_regenerate:
        RequestRevision(newRev)

def RequestRevision(self: Revision):
    """Requests a revision to be generated.
    
    If the parent revision is not ONDISKPUBLISHED, it will recursively 
    request the parent revisions to be generated.
    
    Edition it belongs to must be of type GENERATED and have a generation config."""
    validate_generation_config(self.belongs_to)
    match self.status:
        case RevisionStatus.REQUESTABLE:
            self.status = RevisionStatus.JOBSCHEDULED
        case RevisionStatus.UNFINISHED:
            raise ValueError("Unfinished revision is requested. Illegal operation, can only call request to OnDisk, JobScheduled or Requestable revisions. Revision ID: " + str(Revision.pk))
        case _:
            return
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
        QueueGenerationJobForRevision(self)
    else:
        RequestRevision(latestParentRevision)

def QueueGenerationJobForRevision(self: Revision):
    """Queues a revision job for generation."""
    validate_generation_config(self.belongs_to)
    if self.status != RevisionStatus.JOBSCHEDULED:
        raise IntegrityError("Revision is not in a state to be queued for generation. Revision ID: " + str(self.pk))
    async_task('archive_backend.jobs.generate_revisions', pkStringList([self]),
               task_name=("Generating revision for edition: " + self.belongs_to.title)[:100])