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

        @classmethod
        def fixAllAliases(cls):
            """Operation which fixes any missing aliases. Expensive operation."""
            #Note, it is more performant to do this in a single raw query, but that will break parity with different database backends

            #Creating identity indirections
            #Needs only be done once per call because the other acts do not introduce new ids
            allOrigins = cls.objects.values('origin').distinct()
            batched_bulk_create_boolresult((cls(origin_id = i["origin"], target_id = i["origin"]) for i in allOrigins), 
                       cls, ignore_conflicts=True)
            

            didChange = True
            while didChange: #Repeat until no new entries have been created
                didChange = False

                #Create inverted indirections of existing aliases
                all_non_identity_aliases = cls.objects.exclude(origin=F('target'))
                didChange = didChange or batched_bulk_create_boolresult((cls(origin = item.target, target = item.origin) for item in all_non_identity_aliases), 
                                                             cls, ignore_conflicts=True)

                #Joining target on targets origin to create next level of indirections
                single_item_indirected = lambda item: (cls(origin = item.origin, target = indirection.target) for indirection in item.target.alias_origin_end.all())
                all_indirections_joined_once = itertools.chain(*(single_item_indirected(item) for item in all_non_identity_aliases))

                didChange = didChange or batched_bulk_create_boolresult(all_indirections_joined_once, 
                                                             cls, ignore_conflicts=True)
            
            #fix up alias identifiers
            cls.fixAllAliasIdentifiers()

    return AbstractAliasThrough_
