from django.db import models

class JobStatus(models.IntegerChoices):
    pending = 0
    running = 1
    completed = 2
    failed = 3

class Job(models.Model):
    """Table containing all batch jobs, such as synching files, autogenerating, etc."""
    job_name = models.CharField(max_length=255)
    status = models.IntegerField(choices=JobStatus.choices, default=JobStatus.pending, blank=True)
    parameters = models.JSONField()
    result = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
  