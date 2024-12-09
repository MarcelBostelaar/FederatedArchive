from django.db import models
from model_utils import FieldTracker
from archive_backend.constants import *

class GenerationConfig(models.Model):
    name = models.CharField(max_length=100)
    registered_name = models.CharField(max_length=100)
    description = models.CharField(max_length=500, blank=True)
    automatically_regenerate = models.BooleanField(default=False)

    config_json = models.JSONField(default=dict, blank=True)
    next_step = models.ForeignKey('GenerationConfig', on_delete=models.CASCADE, related_name='previous_steps', null=True, blank=True)
    make_new_generated_revision_filter = models.CharField(max_length=100, blank=False, default="always")

    field_tracker = FieldTracker(['registered_name', 'automatically_regenerate', 'config_json', 'next_step', 'make_new_generated_revision_filter'])