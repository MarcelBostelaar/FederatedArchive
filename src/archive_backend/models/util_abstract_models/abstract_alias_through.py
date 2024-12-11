import datetime
from itertools import islice
import itertools
import string
import uuid
import warnings
from django.apps import apps
from django.db import models
from django.db.models import F
from archive_backend.constants import *
from archive_backend.utils.small import batched_bulk_create_boolresult

def _AbstractAliasThrough(aliasedClassName):
    """Class generator for an alias through table for the aliasedClassName argument. Used as a parent class for all concrete through table models."""
    class AbstractAliasThrough_(models.Model):
        origin = models.ForeignKey(aliasedClassName, on_delete=models.CASCADE, related_name = "alias_origin_end")
        target = models.ForeignKey(aliasedClassName, on_delete=models.CASCADE, related_name = "alias_target_end")

        class Meta:
            unique_together = ["origin", "target"]
            abstract = True

        def __str__(self):
            return f" {self.origin} -> {self.target}"

    return AbstractAliasThrough_
