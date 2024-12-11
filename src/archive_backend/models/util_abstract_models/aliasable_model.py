from itertools import chain
import string
import uuid
from django.db.models import Q
from django.db import models
from archive_backend.constants import *
from archive_backend.utils.small import batched_bulk_create_boolresult, flatten
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
        """Parent model for all models that can have aliases.
        
        Contains all functionality to allow an entry to be an alias of another entry of the same type.
        
        Attributes:
        alias_identifier     Internal value used for keeping track of and speeding up alias collections. Very volatile, do not rely on it for anything.
        """
        
        alias_identifier = models.UUIDField(blank=True, null=True)
        
        def save(self, *args, **kwargs):
            newItem = self._state.adding
            super(AliasableModel_, self).save(*args, **kwargs)
            if newItem:
                self.__fixAlias()
        
        def synchableFields(cls):
            return super().synchableFields() - set(["alias_identifier"])
        
        @classmethod
        def groupByAlias(cls, items):
            """Groups a list of items together with their aliases. Returns a list of lists of items."""
            alias_identifiers = set([item.alias_identifier for item in items])
            return [[item for item in items if item.alias_identifier == alias_id] for alias_id in alias_identifiers]

        @classmethod
        def fixAllAliases(cls):
            """Operation which fixes any missing aliases. Expensive operation."""
            cls.objects.all().update(alias_identifier = None)
            item = cls.objects.filter(alias_identifier = None).first()
            while item is not None:
                item.__fixAlias()
                item = cls.objects.filter(alias_identifier = None).first()

        def __fixAlias(self):
            """Fixes alias indirection for items connected to this specific item directly. Use when updating aliases related to this model.
            
            Relies on the alias identifier of the item to fix up being different from its own.
            """
            alias_id = uuid.uuid4()
            self.alias_identifier = alias_id
            self.save()

            #Repeatedly sets the alias id of all items connected to items with the new id to the new alias id, until no more items are updated.
            #Then creates all possible connections between the items with the new alias id.

            cls = self.__class__

            update_count = 1 #set to 1 just so it isnt zero
            while update_count > 0:
                #If item does not have same alias id already, but is connected to an item that does, set its alias id to the new one.
                update_count = (cls.objects.exclude(alias_identifier = alias_id)
                                .filter(
                                    Q(alias_target_end__origin__alias_identifier = alias_id) 
                                        | #OR
                                    Q(alias_target_end__target__alias_identifier = alias_id))
                                .update(alias_identifier = alias_id))

            all_items = cls.objects.filter(alias_identifier = alias_id)
            #Create (or if it exists, skip in bulk created) every possible alias between the group members
            connections = flatten([[throughTableClassObject(origin = o, target = t) for o in all_items] for t in all_items])
            throughTableClassObject.objects.bulk_create(connections, ignore_conflicts=True)
            
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
