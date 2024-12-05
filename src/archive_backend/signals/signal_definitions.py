from django.dispatch import receiver
from archive_backend.jobs.util import pkStringList
from archive_backend.models import *
from archive_backend.signals.create_generated_revision import CreateGeneratedRevision, RequestRevision
from .util import not_new_items, post_save_change_in_values, post_save_new_item, post_save_new_values, post_save_old_values, pre_save_change_in_values, pre_save_new_values, pre_save_old_values
from django.db.models.signals import post_delete, pre_save, post_save
from django_q.tasks import async_task

##RemotePeer
@receiver(pre_save, sender=RemotePeer)
@pre_save_change_in_values("mirror_files")
@pre_save_new_values(mirror_files = True)
def RemotePeerStartMirroring(sender = None, instance = None, *args, **kwargs):
    EditionsToMirror = list(Edition.objects.filter(from_remote = instance))
    if(len(EditionsToMirror) == 0):
        return
    async_task('archive_backend.jobs.download_latest_revision_for_editions', pkStringList(EditionsToMirror), 
               task_name=("Start mirroring from " + instance.site_name)[:100])

##Edition

#Changes in generation config or parent edition is changed
@receiver(post_save, sender=Edition)
@post_save_change_in_values("generation_config")
def AutogenConfigChanged(instance = None, *args, **kwargs):
    if instance.auto_generation_config is not None:
        CreateGeneratedRevision(instance)
        
@receiver(post_save, sender=Edition)
@post_save_change_in_values("actively_generated_from")
def AutogenConfigChanged(instance = None, *args, **kwargs):
    if instance.actively_generated_from is not None:
        CreateGeneratedRevision(instance)

#New edition with generation config and parent edition

@receiver(post_save, sender=Edition)
@post_save_new_item()
@post_save_new_values(existance_type = existanceType.GENERATED)
def NewGeneratedEdition(instance = None, *args, **kwargs):
    CreateGeneratedRevision(instance)

# Existance type transitions
#Generated -> Local
@receiver(pre_save, sender=Edition)
@pre_save_old_values(existance_type = existanceType.GENERATED)
@pre_save_new_values(existance_type = existanceType.LOCAL)
def IntegrityRemoveGenConfigs(sender = None, instance = None, *args, **kwargs):
    instance.auto_generation_config = None
    instance.actively_generated_from = None

#Local -> Generated
@receiver(post_save, sender=Edition)
@post_save_old_values(_existance_type = existanceType.LOCAL)
@post_save_new_values(_existance_type = existanceType.GENERATED)
def EditionStartGenerating(sender = None, instance = None, created = None, *args, **kwargs):
    CreateGeneratedRevision(instance)
    
#Remote -> MirroredRemote
@receiver(post_save, sender=Edition)
@post_save_old_values(_existance_type = existanceType.REMOTE)
@post_save_new_values(_existance_type = existanceType.MIRROREDREMOTE)
def EditionToMirroredTransition(sender = None, instance = None, *args, **kwargs):
    RequestableRevision = CreateGeneratedRevision(instance)
    RequestRevision(RequestableRevision)

##Revision
@receiver(post_save, sender=Revision)
@post_save_new_item()
def NewRevisionEvent(instance = None, *args, **kwargs):
    for dependency in instance.belongs_to.generational_dependencies:
        CreateGeneratedRevision(dependency)

@receiver(post_save, sender=Revision)
@post_save_change_in_values("status")
@post_save_new_item(status=RevisionStatus.ONDISKPUBLISHED)
def RevisionPublished(instance = None, *args, **kwargs):
    for dependency in instance.belongs_to.generational_dependencies:
        CreateGeneratedRevision(dependency) # Make a new generated revision for all dependencies

    for oldRevision in instance.belongs_to.revisions.exclude(is_backup_revision = True).order_by("-date")[1:]:
        oldRevision.delete() # Delete all non-backup revisions except the latest one

##GenerationConfig
@receiver(post_save, sender=GenerationConfig)
@post_save_change_in_values("script_name", "automatically_regenerate", "source_file_format", "target_file_format", "config_json")
def GenerationConfigChanged(instance = None, *args, **kwargs):
    for edition in instance.editions:
        CreateGeneratedRevision(edition)

