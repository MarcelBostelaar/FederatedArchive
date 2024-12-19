import datetime
from django.db import models
from model_utils import FieldTracker
from archive_backend.constants import *
from .util_abstract_models import RemoteModel

class RemotePeer(RemoteModel):
    site_name = models.CharField(max_length=titleLength)
    site_adress = models.CharField(max_length=maxFileNameLength)
    mirror_files = models.BooleanField(blank=True, default=False)
    last_checkin = models.DateTimeField(blank=True, default=datetime.datetime(1971, 1, 1, 0, 0, 0, 0, tzinfo=datetime.timezone.utc))
    is_this_site = models.BooleanField(blank=True, default=False)

    #Override from_remote because it must be able to self_reference
    from_remote = models.ForeignKey("RemotePeer", blank=True, null=True, on_delete=models.CASCADE)
    

    field_tracker = FieldTracker(fields=["mirror_files"])

    def synchableFields(self):
        return super().synchableFields() - set(["is_this_site", "last_checkin", "mirror_files"])

    def __str__(self) -> str:
        return self.site_name + " - " + self.site_adress
  