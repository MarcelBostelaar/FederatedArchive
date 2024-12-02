

from archive_backend.suggestions.util import stringify_and_concatenate
from archive_backend.models.file_format import FileFormat
from suggestion_manager.abstract_suggestion import AbstractSuggestion, UUIDListType, serializeMultipleUUIDs
from suggestion_manager.models import SuggestedAction, SuggestionStatus

class AbstractAliasSuggestion(AbstractSuggestion):
    SuggestionType: str = "AbstractAliasSuggestion"
    Unprocessed: list 
    Accepted: list
    Rejected: list
    
    def getTitle(self, items):
        raise NotImplementedError("getTitle must be implemented by subclasses.")

    def post_execution(self):
        """Cleans suggestion, for example, splitting off the accepted parts into its own suggestion."""
        #TODO filter unprocessed to check if they are already part of the same alias group
        if len(self.Unprocessed) > 0:
            self.__class__(Unprocessed = self.Unprocessed)\
                .save(title=self.getTitle(self.Unprocessed))
        if len(self.Rejected) > 0:
            item = self.__class__(Rejected = self.Rejected)\
                .save(title=self.getTitle(self.Rejected))
            if item.DatabaseEntry is not None:
                item.DatabaseEntry.status = SuggestionStatus.rejected
                item.DatabaseEntry.save()
        if len(self.Accepted) > 0:
            item = self.__class__(Accepted = self.Accepted)\
                .save(title=self.getTitle(self.Accepted))
            if item.DatabaseEntry is not None:
                item.DatabaseEntry.status = SuggestionStatus.accepted
                item.DatabaseEntry.save()
        self.DatabaseEntry.delete()
    
    def execute_suggestion(self):
        """Executes the suggestion."""
        if len(self.Accepted) > 1:
            first = self.Accepted.pop(0)
            for x in self.Accepted:
                first.addAlias(x)
    
    def should_be_added(self):
        """Returns true if unprocessed suggestions are not a subset of a previously rejected set."""
        return SuggestedAction.objects.filter(data__contains=
                                       {
                                             "SuggestionType": self.SuggestionType,
                                             "Rejected": serializeMultipleUUIDs(self.Unprocessed)
                                       }).count() == 0

class AliasFileFormatSuggestion(AbstractAliasSuggestion):
    SuggestionType: str = "AliasFileFormat"
    Unprocessed: UUIDListType(FileFormat) # type: ignore
    Accepted: UUIDListType(FileFormat) = [] # type: ignore
    Rejected: UUIDListType(FileFormat) = [] # type: ignore
    
    def getTitle(self, items):
        return stringify_and_concatenate(["Alias file formats: "] + [x.format for x in items], 255)