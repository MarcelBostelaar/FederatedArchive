from typing import Iterable
from django.db import models
from django.db.models import Count, Q

from archive_backend.models.file_format import FileFormat

class SuggestionStatus(models.IntegerChoices):
    unprocessed = 0
    rejected = 1
    accepted = 2

class SuggestedAction(models.Model):
    """Table containing suggested actions to approve or disapprove."""
    title = models.CharField(max_length=255)
    description = models.TextField()
    data = models.JSONField(default=dict, blank=True)
    creation = models.DateTimeField(auto_now_add=True, blank=True)
    status = models.IntegerField(choices=SuggestionStatus.choices, default=SuggestionStatus.unprocessed)

    def execute_suggestion(self):
        raise NotImplementedError("execute_suggestion must be implemented by subclasses.")
    
    def should_be_added(self):
        raise NotImplementedError("should_be_added must be implemented by subclasses.")

    def save(self, **kwargs) -> None:
        if not self.should_be_added():
            return
        return super().save(**kwargs)

    class Meta:
        abstract = True

class AliasSuggestion(SuggestedAction):
    unprocessed = models.ManyToManyField(FileFormat)
    rejected = models.ManyToManyField(FileFormat)
    accepted = models.ManyToManyField(FileFormat)

    def post_execution(self):
        #TODO filter unprocessed to check if they are already part of the same alias group
        if self.unprocessed.count() > 0:
            self.__class__(unprocessed=self.unprocessed).save()
        if self.rejected.count() > 0:
            self.__class__(rejected=self.rejected).save()
        if self.accepted.count() > 0:
            self.__class__(accepted=self.accepted).save()
        self.delete()
    
    def execute_suggestion(self):
        if self.accepted.count() > 1:
            items = list(self.accepted.all())
            first = items.pop(0)
            for x in items:
                first.addAlias(x)
        self.post_execution()

    def should_be_added(self):
        # A query that checks if the unprocessed alias suggestions are not a subset of a previously rejected set.
        items = (AliasSuggestion.objects
                .annotate(matching_rejected=Count('rejected', filter=Q(rejected__in=set(self.unprocessed)))) # annotate value "matching_rejected" on every suggestion of this type, set it to the count of rejected items that are in the unprocessed set of the current object"
                .filter(matching_rejected=len(self.unprocessed))) # If the count of matching rejected items is equal to the length of the unprocessed set, then the unprocessed set is a subset of the rejected set
        return items.count() == 0 # if no items match, there is no superset that was rejected, thus this suggestion is possible valid