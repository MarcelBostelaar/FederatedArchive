import datetime
from django.db import models
from ArchiveBackend.constants import *
from .modelsAbstract import RemoteModel

class RemotePeer(RemoteModel):
    site_name = models.CharField(max_length=titleLength)
    site_adress = models.CharField(max_length=maxFileNameLength)
    mirror_files = models.BooleanField(blank=True, default=False)
    last_checkin = models.DateTimeField(blank=True, default=datetime.datetime(1970, 1, 1, 0, 0, 0, 0))
    is_this_site = models.BooleanField(blank=True, default=False)

    exclude_fields_from_synch = ["is_this_site", "last_checkin", "mirror_files"]

    def __str__(self) -> str:
        return self.site_name + " - " + self.site_adress
  