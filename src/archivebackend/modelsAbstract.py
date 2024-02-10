import inspect
from multiprocessing import connection
import os
import re
import string
import uuid
from django.apps import AppConfig
from django.db import models
from django.db.models import Subquery, F
from ArchiveSite.settings import DATABASETYPE, DatabaseBackend
from archivebackend import constants
from archivebackend.constants import *
from archivebackend.settings import CustomDBAliasIndirectionFix, CustomDBIdentityCreationCommand
from django.core import serializers


class _RemoteModel(models.Model):
    """Contains fields and functionality to turn a model remote mirrorable. By using a UUID any two databases of this type can be merged without ID conflicts."""
    from_remote = models.ForeignKey("RemotePeer", blank=True, null=True, on_delete=models.CASCADE)
    # Using UUIDs as primary keys to allows the direct merging of databases without pk and fk conflicts (unless you're astronimically unlucky, one would need to generate 1 billion v4 UUIDs per second for 85 years to have a 50% chance of a single collision).
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    @classmethod
    def __synchableFields(cls):
        return [x for x in cls._meta.get_fields() if x.name not in cls._meta.exclude_fields_from_synch]

    @staticmethod
    def __writeSyncFile(set, basename, fieldsToSync):
        json_serializer = serializers.get_serializer("json")()
        file = None
        for entry in set.iterator():
            fileNum = 0
            counter = 0
            if counter == 0:
                file = open(basename + (fileNum + 1) + ".json", "w")
                file.write("[")
            if counter == constants.maxSyncFileItems:
                file.write("]")
                file.close()
                counter = 0
                fileNum += 1

            file.write(json_serializer.serialize(entry, fields=fieldsToSync))

            if counter < constants.maxFileNameLength:
                file.write(",")
            counter += 1

    @classmethod
    def createSyncFiles(cls):
        classname = cls.__name__
        localFile = os.path.join(constants.syncFileFolder, "local" + classname)
        peersOfPeersFile = os.path.join(constants.syncFileFolder, "peersAndLocal" + classname)

        if not os.path.exists(constants.syncFileFolder):
            os.makedirs(constants.syncFileFolder)

        matches = lambda x: re.compile(classname + r"[0-9]+\.json", re.IGNORECASE).search(x) is not None
        for i in os.listdir(constants.syncFileFolder):
            if matches(i):
                os.remove(i)
        fieldsToSync = cls.__synchableFields()
        cls.__writeSyncFile(cls.objects.all(), peersOfPeersFile, fieldsToSync)
        cls.__writeSyncFile(cls.objects.filter(from_remote = constants.localRemoteID), localFile, fieldsToSync)

    class Meta:
        abstract = True
        exclude_fields_from_synch = []

def _AbstractAliasThrough(aliasedClassName, throughname):
    """The model from which each through table for aliasing derives, containing all functionality."""
    class AbstractAliasThrough_(models.Model):
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

            with connection.cursor() as cursor:
                #Inserting reserve indirections
                match DATABASETYPE:
                    case DatabaseBackend.SQLITE:
                        cursor.execute("""insert or ignore into {} (target, origin)
                                            select 
                                                origin, target
                                            from
                                            (SELECT origin, target FROM {} WHERE target != origin)""".format(throughname, throughname))

                    case DatabaseBackend.CUSTOM:
                        CustomDBAliasIndirectionFix()
                    case _:
                        #TODO
                        raise NotImplementedError("No database agnostic implementation made for inserting reverse indirections.")

                #Join indirect aliases
                match DATABASETYPE:
                    case DatabaseBackend.SQLITE:
                        cursor.execute("""insert or ignore into {} (origin, target)
                                            select 
                                                origin, target
                                            from
                                            (SELECT a.origin, b.target
                                            FROM {} as a
                                            INNER JOIN {} as b ON a.target = b.origin);""".format(throughname,throughname,throughname))

                    case DatabaseBackend.CUSTOM:
                        CustomDBAliasIndirectionFix()
                    case _:
                        #TODO
                        raise NotImplementedError("No database agnostic implementation made for fixing indirection.")
                        

                #Creating identity entries
                match DATABASETYPE:
                    case DatabaseBackend.SQLITE:
                        cursor.execute("""INSERT INTO {} (a, b)
                                            SELECT a, a FROM (
                                                SELECT a FROM {}
                                                EXCEPT
                                                SELECT a FROM {} WHERE a = b
                                            );""")
                    case DatabaseBackend.CUSTOM:
                        CustomDBIdentityCreationCommand()
                    case _:
                        to_be_created = cls.objects.exclude(origin__in=Subquery(cls.objects.filter(origin=F("target"))))
                        cls.objects.bulk_create([_AbstractAliasThrough(origin=to_be_created.origin, target=to_be_created.origin)])


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