import datetime
import uuid
from django.apps import apps
from django.db import models
from archive_backend.constants import *

class RemoteModel(models.Model):
    """Contains fields and functionality to turn a model remote mirrorable. By using a UUID any two databases of this type can be merged without ID conflicts."""
    
    def getLocalSite():
        """Gets the local singleton RemotePeer object. Local peer object is used for all local files."""
        return apps.get_model(app_label="archive_backend", model_name="RemotePeer").objects.get(is_this_site = True)
    
    from_remote = models.ForeignKey("RemotePeer", blank=False, null=False, on_delete=models.CASCADE, default=getLocalSite)
    last_updated = models.DateTimeField(blank=True, auto_now_add=True)
    # Using UUIDs as primary keys to allows the direct merging of databases without pk and fk conflicts (unless you're astronimically unlucky, one would need to generate 1 billion v4 UUIDs per second for 85 years to have a 50% chance of a single collision).
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=True)
    
    class Meta:
        abstract = True
    
    def synchableFields(self):
        """Returns a list of fields that should be considered when syncing this model. Override this method to exclude fields from syncing."""
        return set([x.name for x in self.__class__._meta.fields]) - set(["last_updated"])

    def save(self, *args, **kwargs):
        """Skips syncing the last_updated field if the item is new and sets it to the current time if it has been updated."""
        fields = self.synchableFields()

        if self._state.adding: #new instance
            self.last_updated = datetime.datetime.now()
        else:
            old = type(self).objects.get(id = self.id)

            for key in fields:
                if getattr(old, key) != getattr(self ,key):
                    self.last_updated = datetime.datetime.now()
                    break
        super(RemoteModel, self).save(*args, **kwargs)
