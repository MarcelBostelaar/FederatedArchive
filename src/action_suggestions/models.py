from django.db import models

from archive_backend.models.file_format import FileFormat

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

class AliasFileFormats(SuggestedAction):
    unprocessed = models.ManyToManyField(FileFormat, related_name="+", blank=True)
    rejected = models.ManyToManyField(FileFormat, related_name="+", blank=True)
    accepted = models.ManyToManyField(FileFormat, related_name="+", blank=True)

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