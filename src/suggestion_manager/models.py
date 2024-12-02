from datetime import datetime
from django.db import models

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

  