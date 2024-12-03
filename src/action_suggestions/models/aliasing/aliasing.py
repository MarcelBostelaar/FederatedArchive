from django.db import models
from django.db.models.signals import m2m_changed

from action_suggestions.models.base_suggestion import SuggestedAction, SuggestionStatus
from .validation_signal import AliasSuggestionSignal
from archive_backend.models import AbstractDocument, Author, FileFormat, Language

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
                new = self.__class__(status=SuggestionStatus.unprocessed)
                new.save()
                new.unprocessed.set(self.unprocessed.all())
                new.save()
            if self.rejected.count() > 0:
                new = self.__class__(status=SuggestionStatus.rejected)
                new.save()
                new.rejected.set(self.rejected.all())
                new.save()
            if self.accepted.count() > 0:
                new = self.__class__(status=SuggestionStatus.accepted)
                new.save()
                new.accepted.set(self.accepted.all())
                new.save()
            self.delete()
        
        def execute_suggestion(self):
            if self.accepted.count() > 1:
                items = list(self.accepted.all())
                first = items.pop(0)
                for x in items:
                    first.addAlias(x)
            self.post_execution()

    #Register signal
    m2m_changed.connect(AliasSuggestionSignal, sender=genericAliasSuggestion_.rejected.through)
    m2m_changed.connect(AliasSuggestionSignal, sender=genericAliasSuggestion_.accepted.through)
    m2m_changed.connect(AliasSuggestionSignal, sender=genericAliasSuggestion_.unprocessed.through)
    return genericAliasSuggestion_

class AliasAbstractDocument(GenericAliasSuggestion(AbstractDocument)):
    pass
class AliasAuthor(GenericAliasSuggestion(Author)):
    pass
class AliasLanguage(GenericAliasSuggestion(Language)):
    pass
class AliasFileFormat(GenericAliasSuggestion(FileFormat)):
    pass