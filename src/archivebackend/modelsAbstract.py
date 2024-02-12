import datetime
import inspect
from multiprocessing import connection
import os
import re
import string
import uuid
from django import apps
from django.apps import AppConfig
from django.db import IntegrityError, models
from django.db.models import Subquery, F
from ArchiveSite.settings import DATABASETYPE, DatabaseBackend
from archivebackend import constants
from archivebackend.constants import *
from archivebackend.settings import CustomDBAliasIndirectionFix, CustomDBIdentityCreationCommand
from django.core import serializers
from urllib.request import urlopen 
import json 

def readJsonFromUrl(url):
    response = urlopen(url)
    data_json = json.loads(response.read())
    return data_json

class RemoteModel(models.Model):
    """Contains fields and functionality to turn a model remote mirrorable. By using a UUID any two databases of this type can be merged without ID conflicts."""
    from_remote = models.ForeignKey("RemotePeer", blank=True, null=True, on_delete=models.CASCADE)
    last_updated = models.DateTimeField(blank=True, auto_now_add=True)
    # Using UUIDs as primary keys to allows the direct merging of databases without pk and fk conflicts (unless you're astronimically unlucky, one would need to generate 1 billion v4 UUIDs per second for 85 years to have a 50% chance of a single collision).
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    def save(self, *args, **kwargs):
        if self.id is not None:
            fields = self.__synchableFields().remove("last_updated")
            old = self.objects.get(self.id)

            for key in fields:
                if old[key] != self[key]:
                    self.last_updated = datetime.datetime.now()
                    break
        super(self.__class__, self).save(*args, **kwargs)

    @classmethod
    def __synchableFields(cls):
        return [x for x in cls._meta.get_fields() if x.name not in cls._meta.exclude_fields_from_synch]

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

    @staticmethod
    def __handlePulledItem(cls, item):
        if cls.objects.exists(id=item.id):
            # Item with this is exists in the db
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

    class Meta:
        abstract = True
        exclude_fields_from_synch = []

def _AbstractAliasThrough(aliasedClassName, throughname):
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
            #Future feature, add database specific raw implementations for performance
            ownRemote = apps.get_model(app_label="archiveBackend", model_name="Remote").objects.filter(is_this_site = True)

            with connection.cursor() as cursor:
                #Inserting reserve indirections
                match DATABASETYPE:
                    case DatabaseBackend.SQLITE:
                        cursor.execute("""insert or ignore into {tablename} (target, origin, from_remote, last_updated)
                                            select 
                                                origin, target, %s, DATE('now')
                                            from
                                            (SELECT origin, target FROM {tablename} WHERE target != origin)""".format(tablename = throughname), [ownRemote.id])

                    case DatabaseBackend.CUSTOM:
                        CustomDBAliasIndirectionFix()
                    case _:
                        #TODO
                        raise NotImplementedError("No database agnostic implementation made for inserting reverse indirections.")

                #Join indirect aliases
                match DATABASETYPE:
                    case DatabaseBackend.SQLITE:
                        cursor.execute("""insert or ignore into {tablename} (origin, target, from_remote, last_updated)
                                            select 
                                                origin, target, %s, DATE('now')
                                            from
                                            (SELECT a.origin, b.target
                                            FROM {tablename} as a
                                            INNER JOIN {tablename} as b ON a.target = b.origin);""".format(tablename = throughname), [ownRemote.id])

                    case DatabaseBackend.CUSTOM:
                        CustomDBAliasIndirectionFix()
                    case _:
                        #TODO
                        raise NotImplementedError("No database agnostic implementation made for fixing indirection.")
                        

                #Creating identity entries
                match DATABASETYPE:
                    case DatabaseBackend.SQLITE:
                        cursor.execute("""INSERT OR IGNORE INTO {tablename} (origin, target)
                                            SELECT origin, origin, %s, DATE('now') FROM (
                                                SELECT DISTINCT origin FROM {tablename};
                                            );""".format(tablename = throughname), [ownRemote.id])
                    case DatabaseBackend.CUSTOM:
                        CustomDBIdentityCreationCommand()
                    case _:
                        allValues = cls.objects.values('origin').distinct()
                        for i in allValues:
                            try:
                                cls.create(origin = i.origin, target = i.origin, from_remote=ownRemote)
                            except IntegrityError:
                                pass


    return AbstractAliasThrough_

def AliasableModel(nameOfOwnClass: string):
    """Contains functionality to allow an entry to be an alias of another entry of the same type. Magically adds extra -AliasThrough model to the base model.
    nameOfOwnClass: The name of the concrete class which has to have aliasable functionality added to it.
    """

    #Create accompanying through tables for every class
    throughTableName = nameOfOwnClass + "AliasThrough"
    generated = type(throughTableName, (_AbstractAliasThrough(nameOfOwnClass, throughTableName), ),
                     {"__module__" : __name__, "__qualname__" : throughTableName})
    globals()[generated.__name__] = generated

    class AliasableModel_(models.Model):
        @classmethod
        def fixAllAliases(cls):
            """Operation which fixes any missing aliases. Expensive operation."""
            AppConfig.get_model(throughTableName).fixAllAliases()

        def __fixAlias(this):
            """Fixes alias indirection of this specific item. Use when updating aliases related to this model."""
            #TODO implement item specific alias fixing to reduce operation cost.
            this.fixAllAliases()

        def addAlias(this, other):
            if (not inspect.isclass(other)):
                raise TypeError("Value 'other' passed to addAlias must be of type " + nameOfOwnClass + " but is not a class")

            if (other.__class__.__name__ is not nameOfOwnClass):
                raise TypeError("Value 'other' passed to addAlias must be of type " + nameOfOwnClass + " but was " + other.__class__.__name__)

            AppConfig.get_model(throughTableName).update_or_create(origin = this, target = other)
            AppConfig.get_model(throughTableName).update_or_create(origin = other, target = this)
            this.__fixAlias()

        class Meta:
            abstract = True
    return AliasableModel_