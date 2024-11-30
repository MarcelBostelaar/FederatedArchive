import datetime
from django.db import models

from job_manager.jobs_registry import jobConverter


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
    message_log = models.TextField(blank=True, default="")
    updated_at = models.DateTimeField(auto_now=True)

    def getJob(self):
        """Returns the job object."""
        converted = jobConverter(self.parameters)
        converted.DatabaseJob = self
        return converted
    
    def addMessage(self, message):
        """Adds a message to the message log."""
        self.message_log += datetime.datetime.now().strftime("[%Y-%m-%d_%H:%M:%S]: ") + message + "\n"
        self.save()
    
  