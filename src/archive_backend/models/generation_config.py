from django.db import models
from model_utils import FieldTracker
from archive_backend.constants import *
from archive_backend.models.language import Language
from .file_format import FileFormat

class GenerationConfig(models.Model):
    name = models.CharField(max_length=100)
    registered_name = models.CharField(max_length=100)
    description = models.CharField(max_length=500, blank=True)
    automatically_regenerate = models.BooleanField(default=False)

    config_json = models.JSONField(default=dict, blank=True)
    next_step = models.ForeignKey('GenerationConfig', on_delete=models.CASCADE, related_name='previous_steps', null=True, blank=True)

    field_tracker = FieldTracker()