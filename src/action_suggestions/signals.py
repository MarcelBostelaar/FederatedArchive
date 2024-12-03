from logging import warning
from django.db.models import Count, Q
from django.db.models.signals import m2m_changed, pre_save, post_save
from django.dispatch import receiver

from action_suggestions.models import AliasFileFormats
from archive_backend.models import *
from archive_backend.signals.util import not_new_items, pre_save_value_filter



@receiver(m2m_changed, sender=AliasFileFormats.unprocessed.through)
def AliasSuggestionSignal(sender, instance, action, reverse, model, pk_set, **kwargss):
    # A query that checks if the unprocessed alias suggestions are not a subset of a previously rejected set. Removes suggestion if it is.
    if action == "post_add":
        rejected_subset = (AliasFileFormats.objects
                .annotate(matching_rejected=Count('rejected', filter=Q(rejected__in=set(instance.unprocessed.all()))))
                .filter(matching_rejected=instance.unprocessed.all().count()))
        approved_subset = (AliasFileFormats.objects
                .annotate(matching_approved=Count('approved', filter=Q(approved__in=set(instance.unprocessed.all()))))
                .filter(matching_approved=instance.unprocessed.all().count()))
        oldunprocessed_subset = (AliasFileFormats.objects
                .annotate(matching_oldunprocessed=Count('oldunprocessed', filter=Q(oldunprocessed__in=set(instance.unprocessed.all()))))
                .filter(matching_oldunprocessed=instance.unprocessed.all().count()))

        aliasIdentifiers = set([x.alias_identifier for x in instance.unprocessed])

        if rejected_subset.count() > 0 or approved_subset.count() > 0 or oldunprocessed_subset.count() > 0 or len(aliasIdentifiers) == 1:
            # The suggested merge is already a subset of
                # A rejected suggestion set, so we dont need to suggest it again.
                # An approved suggestion set, so it should already be handled (indicated faulty db state).
                # An old unprocessed suggestion set, so it is already pending.
            # Or all unprocessed items have the same identifier and thus are already aliased
            if approved_subset.count() > 0:
                warning.warn("The suggested merge is already a subset of a previous approved merge, possibly indicating that the suggestion database is out of sync and should be refreshed.")
            alias_suggestions = AliasFileFormats.objects.filter(pk=instance.pk)
            alias_suggestions.delete()

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
    i= AliasFileFormats(
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
