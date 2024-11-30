from django.db import models
from ArchiveBackend.constants import *
from .EditionModels import Edition
from .FileFormat import FileFormat

class AutoGenerationConfig(models.Model):
    name = models.CharField(max_length=100)
    script_name = models.CharField(max_length=100)
    description = models.CharField(max_length=500, blank=True)
    automatically_regenerate = models.BooleanField(default=False)
    source_file_format = models.ForeignKey(FileFormat, on_delete=models.CASCADE, related_name='can_be_consumed_by_autogen', null=True)
    target_file_format = models.ForeignKey(FileFormat, on_delete=models.CASCADE, related_name='can_be_generated_by_autogen', null=True)
    config_json = models.JSONField(default=dict)

# Saves all auto generated files with their configuration so they can be regenerated if needed.
class AutoGeneration(models.Model):
    config = models.ForeignKey(AutoGenerationConfig, on_delete=models.CASCADE)
    original = models.ForeignKey(Edition, related_name="generation_dependencies", on_delete=models.CASCADE)
    generated_version = models.OneToOneField(
        Edition,
        on_delete=models.CASCADE,
        primary_key=True,
    )