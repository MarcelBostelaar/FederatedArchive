from django.db import IntegrityError, models
from archive_backend.constants import *
from archive_backend.utils.transactionsafe_fieldtracker import TransactionsafeFieldTracker
from .util_abstract_models import RemoteModel
from .edition import Edition

class RevisionStatus(models.IntegerChoices):
    ONDISKPUBLISHED = 0
    REQUESTABLE = 1
    JOBSCHEDULED = 2
    UNFINISHED = 3
    REMOTEREQUESTABLE = 4
    REMOTEJOBSCHEDULED = 5

class Revision(RemoteModel):
    belongs_to = models.ForeignKey(Edition, on_delete=models.CASCADE, related_name="revisions")
    date = models.DateTimeField(blank=True, auto_now_add=True)
    entry_file = models.ForeignKey("ArchiveFile", null=True, blank=True, on_delete=models.CASCADE)
    status = models.IntegerField(choices=RevisionStatus.choices, default=RevisionStatus.UNFINISHED, blank=True)
    generated_from = models.ForeignKey("Revision", null=True, blank=True, on_delete=models.SET_NULL, related_name="generation_dependencies")
    is_backup = models.BooleanField(blank=True, default=False)

    field_tracker = TransactionsafeFieldTracker(["status"])

    def __str__(self):
        return self.belongs_to.title + " - " + str(self.date) + " - [" + RevisionStatus(self.status).name + "]"

    def save(self, *args, **kwargs):
        #if parent is generated, edition must be local
        is_generated = self.belongs_to.actively_generated_from is not None
        is_generated_self = self.generated_from is not None
        if is_generated != is_generated_self:
            raise IntegrityError("Parent edition is generated but this revision is not!")
        is_local = self.from_remote.is_this_site

        # Edition and revision must have the same origin. IE cannot create local revisions for a remote edition.
        if self.from_remote != self.belongs_to.from_remote:
            raise IntegrityError("Cannot create revisions with a different origin: ", self.from_remote, self.belongs_to.from_remote)

        validate_status_transition(self.field_tracker.previous("status"), self.status)

        # Check if the revision status is valid
        validate_revision_state(self.status, is_local, is_generated)

        return super().save(*args, **kwargs)
        
def validate_status_transition(old_status, new_status):
    if old_status == new_status:
        return
    match [old_status, new_status]:
        case [RevisionStatus.ONDISKPUBLISHED, _]:
            raise ValueError("Cannot change status from ONDISKPUBLISHED")
        case [_, RevisionStatus.UNFINISHED]:
            raise ValueError("Cannot change status to UNFINISHED")
        case _:
            return

def validate_revision_state(status, is_local, is_generated):
    match [status, is_local, is_generated]:
        case [RevisionStatus.REMOTEREQUESTABLE, False, False]:
            pass
        case [RevisionStatus.REMOTEJOBSCHEDULED, False, False]:
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
