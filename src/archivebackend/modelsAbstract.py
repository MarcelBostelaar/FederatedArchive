import datetime
import inspect
from multiprocessing import connection
import os
import re
import string
import uuid
from django.apps import apps
from django.apps import AppConfig
from django.db import IntegrityError, models
from django.db.models import Subquery, F
from ArchiveSite.settings import DATABASETYPE, DatabaseBackend
from archivebackend import constants
from archivebackend.constants import *
from django.core import serializers
from urllib.request import urlopen 
import json 

def readJsonFromUrl(url):
    response = urlopen(url)
    data_json = json.loads(response.read())
    return data_json

class RemoteModel(models.Model):
    """Contains fields and functionality to turn a model remote mirrorable. By using a UUID any two databases of this type can be merged without ID conflicts."""
    from_remote = models.ForeignKey("RemotePeer", blank=False, null=False, on_delete=models.CASCADE)
    last_updated = models.DateTimeField(blank=True, auto_now_add=True)
    # Using UUIDs as primary keys to allows the direct merging of databases without pk and fk conflicts (unless you're astronimically unlucky, one would need to generate 1 billion v4 UUIDs per second for 85 years to have a 50% chance of a single collision).
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    exclude_fields_from_synch = []
    
    class Meta:
        abstract = True
    
    def save(self, *args, **kwargs):
        fields = self.__synchableFields()
        fields = [x for x in fields if x != "last_updated"]

        if self._state.adding: #new instance
            self.last_updated = datetime.datetime.now()
        else:
            old = type(self).objects.get(id = self.id)

            for key in fields:
                if getattr(old, key) != getattr(self ,key):
                    self.last_updated = datetime.datetime.now()
                    break
        super(RemoteModel, self).save(*args, **kwargs)

    @classmethod
    def __synchableFields(cls):
        return [x.name for x in cls._meta.fields if x.name not in cls.exclude_fields_from_synch]

    @classmethod
    def __writeSyncFile(cls, set, fileNameGenerator):
        json_serializer = serializers.get_serializer("json")()
        fieldsToSync = cls.__synchableFields()
        classname = cls.__name__
        file = None
        createdFiles = []
        fileNum = 1
        objects_in_file_counter = 0
        for entry in set.iterator():
            if objects_in_file_counter == 0:
                filename = fileNameGenerator(classname, fileNum)
                createdFiles += [filename]
                file = open(os.path.join(syncFileFolder, filename), "w")
                file.write("[")
            if objects_in_file_counter == constants.maxSyncFileItems:
                file.write("]")
                file.close()
                objects_in_file_counter = 0
                fileNum += 1

            file.write(json_serializer.serialize(entry, fields=fieldsToSync))

            if objects_in_file_counter < constants.maxFileNameLength:
                file.write(",")
            objects_in_file_counter += 1
        
        file = open(os.path.join(syncFileFolder, fileNameGenerator(classname, "index")), "w")
        file.write("[" + ",".join(createdFiles) + "]")
        file.close()

    @classmethod
    def createSyncFiles(cls):
        classname = cls.__name__

        if not os.path.exists(constants.syncFileFolder):
            os.makedirs(constants.syncFileFolder)

        matches = lambda x: re.compile(classname + r"[0-9]+\.json", re.IGNORECASE).search(x) is not None
        for i in os.listdir(constants.syncFileFolder):
            if matches(i):
                os.remove(i)
        cls.__writeSyncFile(cls.objects.all(), peersOfPeersFileBase)
        cls.__writeSyncFile(cls.objects.filter(is_this_site = True), localFileBase)

    def __overrideFromRemote(self):
        """Indicates whether or not this item may be overridden with new data from a remote source. Overridden in child classes"""
        return True

    @staticmethod
    def __handlePulledItem(cls, item):
        if cls.objects.exists(id=item.id):
            # Item with this is exists in the db
            if not item.__overrideFromRemote():
                #Dont override existing with new data, to prevent malicious propagation in backup versions
                return
            dbobj = cls.objects.get(id=item.id)
            if dbobj.last_updated < item.last_updated:
                # Remote has a newer version of this item
                delattr(item, 'id')
                for (key, value) in item:
                    setattr(dbobj, key, value)
                dbobj.save()
        else:
            # Item does not exist in this db
            obj = object.__new__(cls)
            for (key, value) in item:
                setattr(dbobj, key, value)
            obj.save()

    @classmethod
    def pullFromRemote(cls, remote):
        ownRemote = apps.get_model(app_label="archiveBackend", model_name="Remote").objects.filter(is_this_site = True)
        if remote.peers_of_peer:
            indexFile = peersOfPeersFileBase(cls.__name__, "index")
        else:
            indexFile = localFileBase(cls.__name__, "index")
        index_json = readJsonFromUrl(remoteFileLocationBase(remote, indexFile))
        for file in index_json:
            all_data = readJsonFromUrl(remoteFileLocationBase(remote, file))
            for item in all_data:
                if item.id != ownRemote.id:
                    cls.__handlePulledItem(cls, item)

    @classmethod
    def pullFromAllRemotes(cls):
        Remoteclass = apps.get_model(app_label="archiveBackend", model_name="Remote")
        for remote in Remoteclass.objects.filter(is_this_site = False):
            cls.pullFromRemote(remote)

def _AbstractAliasThrough(aliasedClassName):
    """The model from which each through table for aliasing derives, containing all functionality."""
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
    """Contains functionality to allow an entry to be an alias of another entry of the same type. Magically adds extra -AliasThrough model to the base model.
    nameOfOwnClass: The name of the concrete class which has to have aliasable functionality added to it.
    """

    #Create accompanying through tables for every class
    throughTableName = nameOfOwnClass + "AliasThrough"
    generated = type(throughTableName, (_AbstractAliasThrough(nameOfOwnClass), ),
                     {"__module__" : __name__, "__qualname__" : throughTableName})
    globals()[generated.__name__] = generated

    class AliasableModel_(RemoteModel):
        alias_identifier = models.UUIDField(blank=True, null=True)
        
        def save(self, *args, **kwargs):
            newItem = self._state.adding
            super(AliasableModel_, self).save(*args, **kwargs)
            if newItem: 
                self.addAlias(self)
        
        @classmethod
        def __synchableFields(cls):
            parent = super().__synchableFields()
            return [x for x in parent if x != "alias_identifier"]
        
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

        def __fixAlias(this):
            """Fixes alias indirection of this specific item. Use when updating aliases related to this model."""
            #TODO implement item specific alias fixing to reduce operation cost.
            this.fixAllAliases()

        def addAlias(this, other):
            if not isinstance(other, this.__class__):
                raise TypeError("Value 'other' passed to addAlias must be of type " + nameOfOwnClass + " but was " + other.__class__.__name__)
            archiveAppConfig.get_model(throughTableName).objects.get_or_create(
                    origin=this,
                    target=other,
                    defaults={"from_remote": archiveAppConfig.get_model("RemotePeer").objects.get(is_this_site = True)})

        def allAliases(self):
            allWithThisAsOrigin = self.alias_origin_end.all().iterator()
            for x in allWithThisAsOrigin:
                yield x.target

        class Meta:
            abstract = True
    return AliasableModel_

class RemoteBackupModel(RemoteModel):
    """
    Backupable Remote models may be protected from being overridden during a sync
    to prevent propagation of malicious edits in a root archive to its backups, 
    such as with a hostile takeover of the server."""
    is_backup_revision = models.BooleanField(blank=True, default=False)

    class Meta:
        abstract = True

    def __overrideFromRemote(self):
        """Indicated whether or not this instance should be overridden with data from a remote source"""
        #If the item is marked as a backup it should never be overridden with new data from remote
        return not self.is_backup_revision