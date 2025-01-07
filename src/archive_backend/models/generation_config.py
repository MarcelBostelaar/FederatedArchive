from django.db import models
from archive_backend.constants import *
from .util_abstract_models.tracking_mixin import TrackingMixin

class GenerationConfig(models.Model, TrackingMixin):
    name = models.CharField(max_length=100)
    registered_name = models.CharField(max_length=100)
    description = models.CharField(max_length=500, blank=True)
    automatically_regenerate = models.BooleanField(default=False)

    config_json = models.JSONField(default=dict, blank=True)
    next_step = models.ForeignKey('GenerationConfig', on_delete=models.CASCADE, related_name='previous_steps', null=True, blank=True)
    revision_generation_function = models.CharField(max_length=100, blank=False, default="always")