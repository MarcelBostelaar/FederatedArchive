from django.db.models.signals import pre_save
from django.dispatch import receiver

from archive_backend.models import *

from .util import pre_save_change_in_values

# Editions

@receiver(pre_save, sender=Edition)
def IntegrityCheckGenAddition(instance = None, *args, **kwargs):
    config = instance.generation_config
    parent = instance.actively_generated_from
    match [config, parent]:
        case [None, None]:
            return
        case [None, _]:
            raise IntegrityError("Edition has a parent edition but no generation config. Edition ID: " + str(instance.pk))
        case [_, None]:
            raise IntegrityError("Edition has a generation config but no parent edition. Edition ID: " + str(instance.pk))
        
@receiver(pre_save, sender=Edition)
def IntegrityCheckRemoteEditionGeneration(instance = None, *args, **kwargs):
    if instance.remote_peer.is_this_site:
        return #not a remote edition
    config = instance.generation_config
    parent = instance.actively_generated_from
    if config is not None and parent is not None:
        raise IntegrityError("Remote edition cannot have a generation configuration, as it merely mirrors." + str(instance.pk))



# Revisions

@receiver(pre_save, sender=Revision)
def IntegrityCheckGenerationRemote(instance = None, *args, **kwargs):
    """Ensures that generated revisions are not created for remote peers."""
    if instance.remote_peer.is_this_site:
        #Local version
        if instance.belongs_to.actively_generated_from is None:
            if instance.status == RevisionStatus.REQUESTABLE:
                raise IntegrityError("Tried to create a requestable revision for a local edition with no generation config: " + str(instance.pk))
            if instance.status == RevisionStatus.JOBSCHEDULED:
                raise IntegrityError("Tried to create a job scheduled revision for a local edition with no generation config: " + str(instance.pk))
    else:
        #Remote peer
        if instance.belongs_to.actively_generated_from is not None:
            raise IntegrityError("Cannot create generated revisions for remote editions: " + str(instance.pk))
        
@receiver(pre_save, sender=Revision)
@pre_save_change_in_values("status")
def IntegrityCheckStatusStateTransition(instance = None, *args, **kwargs):
    oldstatus = Revision.objects.get(pk = instance.pk).status
    newstatus = instance.status

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
