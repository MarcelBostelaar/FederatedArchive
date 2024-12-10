import string
import uuid
from django.db import models
from archive_backend.constants import *
from archive_backend.utils.small import batched_bulk_create_boolresult
from .remote_model import RemoteModel
from .abstract_alias_through import _AbstractAliasThrough

def AliasableModel(nameOfOwnClass: string):
    """Class generator for a parent model and an accompanying through table that is used to keep track of aliases.

      Contains all functionality to allow an entry to be an alias of another entry of the same type. 

      Magically creates extra <nameModel>AliasThrough model behind the scenes.

      nameOfOwnClass: The name of the concrete class which has to have aliasable functionality added to it.
    """

    #Create accompanying through tables for every class
    throughTableName = nameOfOwnClass + "AliasThrough"
    throughTableClassObject = type(throughTableName, (_AbstractAliasThrough(nameOfOwnClass), ),
                     {"__module__" : __name__, "__qualname__" : throughTableName})
    globals()[throughTableClassObject.__name__] = throughTableClassObject #Register the class in the global namespace

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
        def fixAllAliasIdentifiers(cls):
            cls.objects.all().update(alias_identifier = None)
            while(True):
                item = cls.objects.filter(alias_identifier = None).first()
                if item is None:
                    return #done
                item.fixAliasIdentifiers()

        def fixAliasIdentifiers(self):
            """Fixed the identifier for a single group to which this items belongs."""
            newUUID= uuid.uuid4()
            self.__class__.objects.filter(target_origin_end__origin__pk=self.pk).update(alias_identifier = newUUID)

        @classmethod
        def fixAllAliases(cls):
            """Operation which fixes any missing aliases. Expensive operation."""
            archiveAppConfig.get_model(throughTableName).fixAllAliases()

        def __fixAlias(self):
            """Fixes alias indirection of this specific item. Use when updating aliases related to this model."""
            cls = self.__class__

            #Creating identity alias
            throughTableClassObject.objects.get_or_create(origin = self, target = self)
            
            didChange = True
            while didChange: #Repeat until no new entries have been created
                didChange = False
                aliases_with_self_as_origin = throughTableClassObject.objects.filter(origin = self).exclude(target=self)

                #Create inverted aliases of existing aliases
                didChange = didChange or batched_bulk_create_boolresult((throughTableClassObject(origin = item.target, target = item.origin) for item in aliases_with_self_as_origin), 
                                                             throughTableClassObject, ignore_conflicts=True)

                #Joining target on targets origin to create next level of alias
                next_levels = (throughTableClassObject(origin = self, target = alias.target) for alias in aliases_with_self_as_origin)

                didChange = didChange or batched_bulk_create_boolresult(next_levels, 
                                                             throughTableClassObject, ignore_conflicts=True)
            
            #fix up alias identifiers
            cls.fixAliasIdentifiers()

        def addAlias(self, other):
            if not isinstance(other, self.__class__):
                raise TypeError("Value 'other' passed to addAlias must be of type " + nameOfOwnClass + " but was " + other.__class__.__name__)
            archiveAppConfig.get_model(throughTableName).objects.get_or_create(
                    origin=self,
                    target=other)
            self.__fixAlias()
            

        def allAliases(self):
            return self.__class__.objects.filter(alias_identifier = self.alias_identifier)

        class Meta:
            abstract = True
    return AliasableModel_
