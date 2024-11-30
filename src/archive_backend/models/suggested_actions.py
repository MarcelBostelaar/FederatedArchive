from django.db import models

class JobStatus(models.IntegerChoices):
    unprocessed = 0
    rejected = 1
    accepted = 2

class SuggestedActions(models.Model):
    """Table containing all batch jobs, such as synching files, autogenerating, etc."""
    title = models.CharField(max_length=255)
    description = models.TextField()
    parameters = models.JSONField()
    creation = models.DateTimeField(auto_now_add=True, blank=True)

  