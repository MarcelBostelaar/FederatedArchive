from django.dispatch import receiver
from archive_backend.jobs.util import pkStringList
from archive_backend.models import *
from .util import not_new_items, pre_save_change_in_values, pre_save_new_values, pre_save_old_values
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

@receiver(pre_save, sender=Edition)
@pre_save_change_in_values("auto_generation_config")
def AutogenConfigChanged(sender = None, instance = None, *args, **kwargs):
    if instance.auto_generation_config is not None:
        async_task('archive_backend.jobs.start_autogeneration_for', pkStringList([instance]),
               task_name=("Autogenerating edition: " + instance.title)[:100])

@receiver(pre_save, sender=Edition)
@pre_save_new_values(actively_generated_from = None)
@pre_save_change_in_values("actively_generated_from")
def ParentEditionNulled(sender = None, instance = None, *args, **kwargs):
    instance.auto_generation_config = None

@receiver(pre_save, sender=Edition)
@pre_save_change_in_values("actively_generated_from")
def ParentEditionChanged(sender = None, instance = None, *args, **kwargs):
    if instance.actively_generated_from is not None:
        async_task('archive_backend.jobs.start_autogeneration_for', pkStringList([instance]),
               task_name=("Autogenerating edition: " + instance.title)[:100])


# Existance type transitions
#AutoGeneration -> Local
@receiver(pre_save, sender=Edition)
@pre_save_new_values(existance_type = existanceType.LOCAL)
@pre_save_old_values(existance_type = existanceType.GENERATED)
def AutogenerationToLocalTransition(sender = None, instance = None, *args, **kwargs):
    if instance.autogeneration is not None:
        instance.delete()
    instance.actively_generated_from = None

#Local -> AutoGeneration
@receiver(pre_save, sender=Edition)
@pre_save_new_values(existance_type = existanceType.GENERATED)
@pre_save_old_values(existance_type = existanceType.LOCAL)
def LocalToAutogenerationTransition(sender = None, instance = None, *args, **kwargs):
    if instance.auto_generation_config is None:
        raise ValueError("An auto generation configuration for this item has not been set")
    async_task('archive_backend.jobs.start_autogeneration_for', pkStringList([instance]),
               task_name=("Autogenerating edition: " + instance.title)[:100])
    
#Remote -> MirroredRemote
@receiver(pre_save, sender=Edition)
@pre_save_new_values(existance_type = existanceType.MIRROREDREMOTE)
@pre_save_old_values(existance_type = existanceType.REMOTE)
def EditionToMirroredTransition(sender = None, instance = None, *args, **kwargs):
    async_task('archive_backend.jobs.download_latest_revision_for_editions', pkStringList([instance]), 
               task_name=("Downloading local files for edition: " + instance.title)[:100])


##Revision
@receiver(post_save, sender=Revision)
def RevisionCleanAndAutogenLaunch(sender = None, instance = None, created = None, *args, **kwargs):
    if not created:
        #Not required for changes to the revision
        return
    if instance.belongs_to.generation_dependencies.count() > 0:
        async_task('archive_backend.jobs.start_autogeneration_for', pkStringList(instance.belongs_to.generation_dependencies.all()),
               task_name=("Autogenerating dependent editions of: " + instance.belongs_to.title)[:100])

    async_task('archive_backend.jobs.delete_old_revisions', pkStringList([instance.belongs_to]), 
               task_name=("Deleting old revisions of edition: " + instance.belongs_to.title)[:100])
