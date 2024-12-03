from django.db import models
from django.db.models.signals import m2m_changed

from action_suggestions.signals.alias_suggestion_signal import AliasSuggestionSignal
from archive_backend.models import AbstractDocument, Author, FileFormat, Language

class SuggestionStatus(models.IntegerChoices):
    unprocessed = 0
    rejected = 1
    accepted = 2

class SuggestedAction(models.Model):
    """Table containing suggested actions to approve or disapprove."""
    title = models.CharField(max_length=255, default="No title", blank=True)
    description = models.TextField(default="No description provided.", blank=True)
    creation = models.DateTimeField(auto_now_add=True, blank=True)
    status = models.IntegerField(choices=SuggestionStatus.choices, default=SuggestionStatus.unprocessed)

    def execute_suggestion(self):
        raise NotImplementedError("execute_suggestion must be implemented by subclasses.")

    class Meta:
        abstract = True

def GenericAliasSuggestion(cls):
    # Generates a model superclass with the cls to operate on added.
    # Automatically register the signal which does validation
    class genericAliasSuggestion_(SuggestedAction):
        unprocessed = models.ManyToManyField(cls, related_name="+", blank=True)
        rejected = models.ManyToManyField(cls, related_name="+", blank=True)
        accepted = models.ManyToManyField(cls, related_name="+", blank=True)

        class Meta:
            abstract = True

        def post_execution(self):
            if self.unprocessed.count() > 0:
                self.__class__(unprocessed=self.unprocessed, status=SuggestionStatus.unprocessed).save()
            if self.rejected.count() > 0:
                self.__class__(rejected=self.rejected, status=SuggestionStatus.rejected).save()
            if self.accepted.count() > 0:
                self.__class__(accepted=self.accepted, status=SuggestionStatus.accepted).save()
            self.delete()
        
        def execute_suggestion(self):
            if self.accepted.count() > 1:
                items = list(self.accepted.all())
                first = items.pop(0)
                for x in items:
                    first.addAlias(x)
            self.post_execution()

    #Register signal
    m2m_changed.connect(AliasSuggestionSignal, sender=cls, weak=True, dispatch_uid=None)
    return genericAliasSuggestion_

class AliasAbstractDocument(GenericAliasSuggestion(AbstractDocument)):
    pass
class AliasAuthor(GenericAliasSuggestion(Author)):
    pass
class AliasLanguage(GenericAliasSuggestion(Language)):
    pass
class AliasFileFormat(GenericAliasSuggestion(FileFormat)):
    pass