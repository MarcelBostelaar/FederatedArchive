from django.dispatch import receiver
from archive_backend.jobs.util import pkStringList
from archive_backend.models import *
from .util import not_new_items, pre_save_value_filter
from django.db.models.signals import pre_delete, pre_save, post_save
from django_q.tasks import async_task

#TODO make post save?
##RemotePeer
@receiver(pre_save, sender=RemotePeer)
# @not_new_items()
@pre_save_value_filter(newValuesMustContain={"mirror_files" : True}, valuesMustHaveChanged=["mirror_files"])
def RemotePeerStartMirroring(sender = None, instance = None, *args, **kwargs):
    EditionsToMirror = list(Edition.objects.filter(from_remote = instance))
    if(len(EditionsToMirror) == 0):
        return
    async_task('archive_backend.jobs.download_latest_revision_for_editions', pkStringList(EditionsToMirror), 
               task_name=("Start mirroring from " + instance.site_name)[:100])

##Edition

#TODO implement post delete

def downloadLatestRevisionFor(instance):
    async_task('archive_backend.jobs.download_latest_revision_for_editions', pkStringList([instance]), 
               task_name=("Making local files for edition: " + instance.title)[:100])

#Any to local
@receiver(pre_save, sender=Edition)
@not_new_items()
@pre_save_value_filter(newValuesMustContain={"existance_type" : existanceType.LOCAL}, valuesMustHaveChanged=["existance_type"])
def EditionToLocalTransition(sender = None, instance = None, *args, **kwargs):
    downloadLatestRevisionFor(instance)
    

#Transition is restricted to remote -> mirrored, so can only be called if previous state is remote
@receiver(pre_save, sender=Edition)
# @not_new_items() #TODO test if new mirrored items are also called by this
@pre_save_value_filter(newValuesMustContain={"existance_type" : existanceType.MIRROREDREMOTE}, valuesMustHaveChanged=["existance_type"])
def EditionToMirroredTransition(sender = None, instance = None, *args, **kwargs):
    downloadLatestRevisionFor(instance)


#Revision
@receiver(post_save, sender=Revision)
def RevisionCleanAndAutogenLaunch(sender = None, instance = None, created = None, *args, **kwargs):
    print("Not implemented signal revision")
    if not created:
        #Not required for changes to the revision
        return
    if instance.belongs_to.generation_dependencies.count() > 0:
        async_task('archive_backend.jobs.start_autogeneration_for', pkStringList(instance.belongs_to.generation_dependencies.all()),
               task_name=("Autogenerating dependent editions of: " + instance.belongs_to.title)[:100])

    async_task('archive_backend.jobs.delete_old_revisions', pkStringList([instance.belongs_to]), 
               task_name=("Deleting old revisions of edition: " + instance.belongs_to.title)[:100])

#TODO make post delete

#Abstract document
#TODO implement post delete


#File
#TODO make post_delete not pre_delete?
@receiver(pre_delete, sender=File)
def OnFileDelete(_model, modelInstance, database, origin, *args, **kwargs):
    print("Not implemented signal file")
    #TODO implement
    pass

