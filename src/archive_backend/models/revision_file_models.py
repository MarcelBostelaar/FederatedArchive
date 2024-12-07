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

        # Check if revision status is valid at all.
        match [is_local, is_generated, self.status]:
            case [True, False, RevisionStatus.REQUESTABLE]:
                raise IntegrityError("Tried to create a requestable revision for a local edition that isn't generated")
            case [True, False, RevisionStatus.JOBSCHEDULED]:
                raise IntegrityError("Tried to create a job scheduled revision for a local edition that isn't generated")
            case [True, True, RevisionStatus.UNFINISHED]:
                raise IntegrityError("Tried to create an unfinished revision for a local edition that is generated. Unfinished status is for manual revisions for manually craftee editions, not generated ones.")
        
        return super().save(*args, **kwargs)


def status_transition_check(oldstatus, newstatus):
    if oldstatus == newstatus:
        return

    match [oldstatus, newstatus]:
        case [RevisionStatus.REQUESTABLE, RevisionStatus.UNFINISHED]:
            raise IntegrityError("Cannot change status to UNFINISHED from REQUESTABLE")
        case [RevisionStatus.UNFINISHED, RevisionStatus.ONDISKPUBLISHED]:
            pass #allowed, but all others from unfinished is not allowed
        case [RevisionStatus.UNFINISHED, _]:
            raise IntegrityError("Cannot change revision status to anything other than ONDISKPUBLISHED from UNFINISHED")
        case [RevisionStatus.JOBSCHEDULED, RevisionStatus.ONDISKPUBLISHED]:
            pass #Allowed, but all others from jobscheduled is not allowed
        case [RevisionStatus.JOBSCHEDULED, _]:
            raise IntegrityError("Cannot change status to anything other than ONDISKPUBLISHED from JOBSCHEDULED")
        case [RevisionStatus.ONDISKPUBLISHED, _]:
            raise IntegrityError("Cannot unpublish a revision by changing status from ONDISKPUBLISHED to anything else")
        case [_, RevisionStatus.REQUESTABLE]:
            raise IntegrityError("Cannot change status to REQUESTABLE after revision creation")