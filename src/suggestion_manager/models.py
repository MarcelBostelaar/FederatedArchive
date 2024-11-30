from django.db import models

class JobStatus(models.IntegerChoices):
    unprocessed = 0
    rejected = 1
    accepted = 2

class SuggestedAction(models.Model):
    """Table containing suggested actions to approve or disapprove."""
    title = models.CharField(max_length=255)
    description = models.TextField()
    parameters = models.JSONField()
    creation = models.DateTimeField(auto_now_add=True, blank=True)

  