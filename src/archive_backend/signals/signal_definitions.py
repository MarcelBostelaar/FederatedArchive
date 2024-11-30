from dataclasses import fields
from django.dispatch import receiver
from archive_backend.jobs.download_edition_job import DownloadLatestRevisionForEditionsJob
from archive_backend.models import *
from job_manager.models import Job
from .util import not_new_items, pre_save_value_filter
from django.db.models.signals import pre_delete, pre_save, post_save


##RemotePeer
@receiver(pre_save, sender=RemotePeer)
# @not_new_items()
@pre_save_value_filter(newValuesMustContain={"mirror_files" : True}, valuesMustHaveChanged=["mirror_files"])
def RemotePeerStartMirroring(sender = None, instance = None, *args, **kwargs):
    EditionsToMirror = Edition.objects.filter(from_remote = instance)
    Job.objects.create(
        job_name = "Start mirroring '" + instance.site_name + "'",
        parameters = DownloadLatestRevisionForEditionsJob(Editions = list(EditionsToMirror)).model_dump()
        )


@receiver(pre_save, sender=RemotePeer)
@not_new_items()
@pre_save_value_filter(newValuesMustContain={"mirror_files" : False}, valuesMustHaveChanged=["mirror_files"])
def RemotePeerStopMirroring(sender = None, instance = None, *args, **kwargs):
    print("Not implemented signal remote peer 2")
    #TODO implement
    pass


##FileFormat
@receiver(pre_save, sender=FileFormat)
def CheckForIdentificalFormat(sender = None, instance = None, *args, **kwargs):
    print("Not implemented signal file format")
    #TODO implement
    pass


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