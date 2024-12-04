from django.db import models
from archive_backend.constants import *
from .edition_models import Edition
from .file_format import FileFormat

class AutoGenerationConfig(models.Model):
    name = models.CharField(max_length=100)
    script_name = models.CharField(max_length=100)
    description = models.CharField(max_length=500, blank=True)
    automatically_regenerate = models.BooleanField(default=False)
    source_file_format = models.ForeignKey(FileFormat, on_delete=models.CASCADE, related_name='can_be_consumed_by_autogen', null=True)
    target_file_format = models.ForeignKey(FileFormat, on_delete=models.CASCADE, related_name='can_be_generated_by_autogen', null=True)
    config_json = models.JSONField(default=dict)