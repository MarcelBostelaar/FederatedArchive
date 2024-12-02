from django.dispatch import receiver
from archive_backend.jobs.util import pkStringList
from archive_backend.models import *
from archive_backend.suggestions.suggestions import AliasFileFormatSuggestion
from .util import not_new_items, pre_save_value_filter
from django.db.models.signals import pre_delete, pre_save, post_save
from django_q.tasks import async_task



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


@receiver(pre_save, sender=RemotePeer)
@not_new_items()
@pre_save_value_filter(newValuesMustContain={"mirror_files" : False}, valuesMustHaveChanged=["mirror_files"])
def RemotePeerStopMirroring(sender = None, instance = None, *args, **kwargs):
    EditionsToStopMirroring = list(Edition.objects.filter(from_remote = instance))
    if(len(EditionsToStopMirroring) == 0):
        return
    async_task('archive_backend.jobs.remove_local_files_for', pkStringList(EditionsToStopMirroring), 
               task_name=("Stop mirroring from " + instance.site_name)[:100])


##FileFormat
@receiver(post_save, sender=FileFormat)
def CheckForIdentificalFormat(sender = None, instance = None, created = None, *args, **kwargs):
    similarItems = list(FileFormat.objects.filter(format__icontains=instance.format))
    if len(similarItems) <= 1:
        return
    aliasIdentifiers = set([x.alias_identifier for x in similarItems])
    if len(aliasIdentifiers) == 1:
        return
    AliasFileFormatSuggestion(Unprocessed = similarItems).save()


##Language
@receiver(pre_save, sender=Language)
def CheckForIdenticalISOcode(sender = None, instance = None, *args, **kwargs):
    print("Not implemented signal language")
    #TODO implement
    pass


##Author
@receiver(pre_save, sender=Author)
def CheckForPossibleAuthorAliases(sender = None, instance = None, *args, **kwargs):
    print("Not implemented signal author")
    #TODO implement
    pass


##AbstractDocument
@receiver(pre_save, sender=AbstractDocument)
def CheckForPossibleDocumentAliases(sender = None, instance = None, *args, **kwargs):
    print("Not implemented signal abstract document")
    #TODO implement
    pass


##Edition

@receiver(pre_save, sender=Edition)
@not_new_items()
@pre_save_value_filter(newValuesMustContain={"existance_type" : existanceType.LOCAL}, valuesMustHaveChanged=["existance_type"])
def EditionToLocalTransition(sender = None, instance = None, *args, **kwargs):
    print("Not implemented signal edition to local")
    #TODO implement
    pass

#Transition is restricted to mirrored -> remote, so can only be called if previous state is remote
@receiver(pre_save, sender=Edition)
@not_new_items()
@pre_save_value_filter(newValuesMustContain={"existance_type" : existanceType.REMOTE}, valuesMustHaveChanged=["existance_type"])
def EditionToRemoteTransition(sender = None, instance = None, *args, **kwargs):
    print("Not implemented signal edition to remote")
    #TODO implement
    pass

#Transition is restricted to remote -> mirrored, so can only be called if previous state is remote
@receiver(pre_save, sender=Edition)
@not_new_items()
@pre_save_value_filter(newValuesMustContain={"existance_type" : existanceType.MIRROREDREMOTE}, valuesMustHaveChanged=["existance_type"])
def EditionToMirroredTransition(sender = None, instance = None, *args, **kwargs):
    print("Not implemented signal edition to mirrored")
    #TODO implement
    pass


#Revision
@receiver(post_save, sender=Revision)
def RevisionCleanAndAutogenLaunch(sender = None, instance = None, created = None, *args, **kwargs):
    print("Not implemented signal revision")
    if not created:
        return
    #TODO implement
    pass


#File
@receiver(pre_delete, sender=File)
def OnFileDelete(_model, modelInstance, database, origin, *args, **kwargs):
    print("Not implemented signal file")
    #TODO implement
    pass


#AutoGenerationConfig
@receiver(pre_save, sender=AutoGenerationConfig)
def AutogenConfigAddRegenAllSuggestion(sender = None, instance = None, *args, **kwargs):
    print("Not implemented signal autogen config")
    #TODO implement
    pass


#AutoGeneration
@receiver(post_save, sender=AutoGeneration)
def AddGenerationJobSuggestion(sender = None, instance = None, created = None, *args, **kwargs):
    if not created:
        return
    print("Not implemented signal autogen")
    #TODO implement
    pass