import datetime
import string
import uuid
import warnings
from django.apps import apps
from django.db import models
from django.db.models import F
from archive_backend.constants import *

class RemoteModel(models.Model):
    """Contains fields and functionality to turn a model remote mirrorable. By using a UUID any two databases of this type can be merged without ID conflicts."""
    
    def getLocalSite():
        """Gets the local singleton RemotePeer object. Local peer object is used for all local files."""
        return apps.get_model(app_label="archive_backend", model_name="RemotePeer").objects.get(is_this_site = True)
    
    from_remote = models.ForeignKey("RemotePeer", blank=False, null=False, on_delete=models.CASCADE, default=getLocalSite)
    last_updated = models.DateTimeField(blank=True, auto_now_add=True)
    # Using UUIDs as primary keys to allows the direct merging of databases without pk and fk conflicts (unless you're astronimically unlucky, one would need to generate 1 billion v4 UUIDs per second for 85 years to have a 50% chance of a single collision).
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
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

def _AbstractAliasThrough(aliasedClassName):
    """Class generator for an alias through table for the aliasedClassName argument. Used as a parent class for all concrete through table models."""
    class AbstractAliasThrough_(RemoteModel):
        origin = models.ForeignKey(aliasedClassName, on_delete=models.CASCADE, related_name = "alias_origin_end")
        target = models.ForeignKey(aliasedClassName, on_delete=models.CASCADE, related_name = "alias_target_end")

        class Meta:
            unique_together = ["origin", "target"]
            abstract = True

        @classmethod
        def fixAllAliases(cls):
            """Operation which fixes any missing aliases. Expensive operation."""
            #Note, it is more performant to do this in a single raw query, but that will break parity with different database backends
            ownRemote = archiveAppConfig.get_model("RemotePeer").objects.get(is_this_site = True)

            # with connection.cursor() as cursor:
            #Creating identity indirections
            #Needs only be done once per call because the other acts do not introduce new ids
            allOrigins = cls.objects.values('origin').distinct()
            for i in allOrigins:
                cls.objects.get_or_create(origin_id = i["origin"], target_id = i["origin"], defaults={"from_remote": ownRemote})

            didChange = True
            while didChange: #Repeat until no new entries have been created
                #START loop
                didChange = False
                for item in cls.objects.exclude(origin=F('target')):
                    #Inserting reserve indirections
                    _, created = cls.objects.get_or_create(origin = item.target, target = item.origin, defaults={"from_remote": ownRemote})
                    didChange = didChange or created

                    #Join indirect aliases
                    for indirection in item.target.alias_origin_end.all():
                        _, created = cls.objects.get_or_create(origin = item.origin, target = indirection.target, defaults={"from_remote": ownRemote})
                        didChange = didChange or created
                #END loop
    return AbstractAliasThrough_

def AliasableModel(nameOfOwnClass: string):
    """Class generator for a parent model and an accompanying through table that is used to keep track of aliases.

      Contains all functionality to allow an entry to be an alias of another entry of the same type. 

      Magically creates extra <nameModel>AliasThrough model behind the scenes.

      nameOfOwnClass: The name of the concrete class which has to have aliasable functionality added to it.
    """

    #Create accompanying through tables for every class
    throughTableName = nameOfOwnClass + "AliasThrough"
    generated = type(throughTableName, (_AbstractAliasThrough(nameOfOwnClass), ),
                     {"__module__" : __name__, "__qualname__" : throughTableName})
    globals()[generated.__name__] = generated #Register the class in the global namespace

    class AliasableModel_(RemoteModel):
        alias_identifier = models.UUIDField(blank=True, null=True)
        
        def save(self, *args, **kwargs):
            newItem = self._state.adding
            super(AliasableModel_, self).save(*args, **kwargs)
            if newItem: 
                self.addAlias(self)
        
        def synchableFields(cls):
            return super().synchableFields() - set(["alias_identifier"])
        
        @classmethod
        def fixAliasIdentifiers(cls):
            cls.objects.all().update(alias_identifier = None)
            while(True):
                item = cls.objects.filter(alias_identifier = None).first()
                if item is None:
                    return #done
                newUUID= uuid.uuid4()
                item.alias_identifier = newUUID
                item.save()
                for x in item.allAliases():
                    x.alias_identifier = newUUID
                    x.save()

        @classmethod
        def fixAllAliases(cls):
            """Operation which fixes any missing aliases. Expensive operation."""
            archiveAppConfig.get_model(throughTableName).fixAllAliases()
            cls.fixAliasIdentifiers()

        def __fixAlias(self):
            """Fixes alias indirection of this specific item. Use when updating aliases related to this model."""
            #TODO implement item specific alias fixing to reduce operation cost.
            warnings.warn("Not implemented fix alias on item, doing expensive operation on entire table instead")
            self.fixAllAliases()

        def addAlias(self, other):
            if not isinstance(other, self.__class__):
                raise TypeError("Value 'other' passed to addAlias must be of type " + nameOfOwnClass + " but was " + other.__class__.__name__)
            archiveAppConfig.get_model(throughTableName).objects.get_or_create(
                    origin=self,
                    target=other,
                    defaults={"from_remote": archiveAppConfig.get_model("RemotePeer").objects.get(is_this_site = True)})
            self.__fixAlias()
            

        def allAliases(self):
            """Returns an iterator of all items that are aliases of this item, including itself."""
            allWithThisAsOrigin = self.alias_origin_end.all().iterator()
            for x in allWithThisAsOrigin:
                yield x.target

        class Meta:
            abstract = True
    return AliasableModel_

class RemoteBackupModel(RemoteModel):
    """
    Backupable Remote models may be protected from being overridden during a sync, or being deleted when a new revision is created, by setting the is_backup flag to True.

    This will prevent propagation of malicious edits in a root archive/source server to its backups/mirrors,
    such as with a hostile takeover of the server.
    
    Alternatively, it may be used for more permantent versioning purposes.
    """
    is_backup = models.BooleanField(blank=True, default=False)

    class Meta:
        abstract = True