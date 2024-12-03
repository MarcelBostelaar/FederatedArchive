from django.db import models

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