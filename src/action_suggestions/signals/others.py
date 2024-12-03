from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from action_suggestions.models import AliasFileFormat
from archive_backend.models import *
from archive_backend.signals.util import not_new_items, pre_save_value_filter

#Edition
#Transition is restricted to mirrored -> remote, so can only be called if previous state is remote
@receiver(pre_save, sender=Edition)
@not_new_items()
@pre_save_value_filter(newValuesMustContain={"existance_type" : existanceType.REMOTE}, valuesMustHaveChanged=["existance_type"])
def EditionToRemoteTransition(sender = None, instance = None, *args, **kwargs):
    print("Not implemented signal edition to remote")
    #TODO implement
    pass

#Remote peer
#TODO make post save?
@receiver(pre_save, sender=RemotePeer)
@not_new_items()
@pre_save_value_filter(newValuesMustContain={"mirror_files" : False}, valuesMustHaveChanged=["mirror_files"])
def RemotePeerStopMirroring(sender = None, instance = None, *args, **kwargs):
    print("Not implemented Remote peer stop mirroring")
    pass #TODO add suggestion to clean now unneccecary files

##FileFormat
@receiver(post_save, sender=FileFormat)
def CheckForIdentificalFormat(sender = None, instance = None, created = None, *args, **kwargs):
    similarItems = list(FileFormat.objects.filter(format__icontains=instance.format))
    if len(similarItems) <= 1:
        return
    aliasIdentifiers = set([x.alias_identifier for x in similarItems])
    if len(aliasIdentifiers) == 1:
        return
    i= AliasFileFormat(
        title="Merge", 
        description="Multiple file formats with similar names have been detected. Please review the following formats: " + ", ".join([x.format for x in similarItems])
        )
    i.save()
    i.unprocessed.set(similarItems)


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


#AutoGenerationConfig
@receiver(pre_save, sender=AutoGenerationConfig)
def AutogenConfigAddRegenAllSuggestion(sender = None, instance = None, *args, **kwargs):
    print("Not implemented signal autogen config")
    #TODO implement
    pass


#AutoGeneration
@receiver(post_save, sender=AutoGeneration)
def AddGenerationSuggestion(sender = None, instance = None, created = None, *args, **kwargs):
    if not created:
        return
    print("Not implemented signal autogen")
    #TODO implement
    pass
