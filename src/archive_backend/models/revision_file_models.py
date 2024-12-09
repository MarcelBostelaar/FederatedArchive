from django.db import IntegrityError, models
from model_utils import FieldTracker
from archive_backend.constants import *
from .edition import Edition
from .util_abstract_models import RemoteBackupModel

class RevisionStatus(models.IntegerChoices):
    ONDISKPUBLISHED = 0
    REQUESTABLE = 1
    JOBSCHEDULED = 2
    UNFINISHED = 3
    REMOTEREQUESTABLE = 4
    REMOTEJOBSCHEDULED = 5

class Revision(RemoteBackupModel):
    belongs_to = models.ForeignKey(Edition, on_delete=models.CASCADE, related_name="revisions")
    date = models.DateTimeField(blank=True, auto_now_add=True)
    entry_file = models.ForeignKey("ArchiveFile", null=True, blank=True, on_delete=models.CASCADE)
    status = models.IntegerField(choices=RevisionStatus.choices, default=RevisionStatus.UNFINISHED, blank=True)

    field_tracker = FieldTracker(["status"])

    def save(self, *args, **kwargs):
        #if parent is generated, edition must be local
        is_generated = self.belongs_to.actively_generated_from is not None
        is_local = self.from_remote.is_this_site

        # Edition and revision must have the same origin. IE cannot create local revisions for a remote edition.
        if self.from_remote != self.belongs_to.from_remote:
            raise IntegrityError("Cannot create revisions with a different origin: ", self.from_remote, self.belongs_to.from_remote)

        # For changes in existing
        if not self._state.adding:
            oldItem = Revision.objects.filter(id = self.pk).first()
            oldstatus = oldItem.status
            newstatus = self.status
            status_transition_check(oldstatus, newstatus)

        # Check if the revision status is valid
        validate_revision_state(self.status, is_local, is_generated)

        return super().save(*args, **kwargs)


def status_transition_check(oldstatus, newstatus):
    if oldstatus == newstatus:
        return

    match [oldstatus, newstatus]:
        case [RevisionStatus.REMOTEREQUESTABLE, RevisionStatus.REQUESTABLE]:
            pass
        case [RevisionStatus.REQUESTABLE, RevisionStatus.JOBSCHEDULED]:
            pass
        case [RevisionStatus.JOBSCHEDULED, RevisionStatus.ONDISKPUBLISHED]:
            pass
        case [RevisionStatus.UNFINISHED, RevisionStatus.ONDISKPUBLISHED]:
            pass
        case _:
            raise IntegrityError("Invalid revision status transition: ", oldstatus, newstatus)
        
def validate_revision_state(status, is_local, is_generated):
    match [status, is_local, is_generated]:
        case [RevisionStatus.REMOTEREQUESTABLE, False, False]:
            pass
        case [RevisionStatus.REQUESTABLE, True, True]:
            pass #Local generated
        case [RevisionStatus.REQUESTABLE, False, False]:
            pass #Remote existing
        case [RevisionStatus.JOBSCHEDULED, True, True]:
            pass #Local generated
        case [RevisionStatus.JOBSCHEDULED, False, False]:
            pass #Remote existing
        case [RevisionStatus.UNFINISHED, True, False]:
            pass
        case [RevisionStatus.ONDISKPUBLISHED, _, _]:
            pass
        case _: raise IntegrityError("Invalid revision state: status:{status}, local:{local}, generated:{generated}".format(status, is_local, is_generated))
