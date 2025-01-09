from datetime import datetime
from typing import List, Tuple
import uuid
from django.forms import ValidationError
from rest_framework import serializers
from archive_backend import utils
from archive_backend.models import RemoteModel
from archive_backend.utils.small import HttpUtil
from .registries import *

class AbstractRemoteSerializer(serializers.ModelSerializer):
    """Utility model serializer subclass that provides functionality to download from a remote to the serializer, with automatically downloading any dependency foreign key items."""

    #Developer reasoning: Hooking into the serializer to override something like to_internal_value 
    # turned out to be near impossible. Overriding is_valid was also very clunky. 
    # Adding custom validators doesnt work either as the default field validator is always 
    # called before the custom validator, which is implemented on the field subclass itself,
    # and thus is not overridable without making custom foreign key field subclasses or custom fields 
    # in the serializers which would only need to modify deserialisation. 
    # This solution by manually pre-downloading dependencies is much less technologically complex 
    # and more loosely coupled by limiting the code to the level of the serializer itself, 
    # all contained in this parent class. No overrides are done, data from the parent class is 
    # only retrieved (and thus easie to detect and fix if the library ever makes a breaking change).

    pagination_class = None

    def get_unique_together_validators(self):
        """Overriding method to disable unique together checks. 
        Done to prevent unique together checks from triggering an exception when updating an existing item.
        Actual unique constraints will be checked by the database itself."""
        return []

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not hasattr(cls.Meta, "abstract") or not cls.Meta.abstract:
            SerializerRegistry.register(cls.Meta.model, cls) #Register all subclasses that arent abstract to the registry

    @classmethod
    def create_or_update_from_remote_data(this_serializer_class_type, data: dict, from_ip: str, recursively_update = False):
        """Attempts to create or update a model instance for this serializer from data retrieved from a remote server.

        Will recursively download all instances of other models this item is dependent on.

        Intended to be used in batch updates when you download a long list of items from a remote.
        Use download_or_update_from_remote_site with an id for retrieving individual items automatically.
        
        :param data A dictionary containing retrieved data
        :param from_ip The ip to download the instance dependencies from
        :param recursively_update Set to True if all instances this item depends on need to be updated. 
        Leave empty or false to only download if there isnt already a copy of it on this server. 
        Provides single-level protection against circular references (only against direct foreign key to self).
        Ensure no circular foreign key references are made in the serializers (or models)."""
        remote_last_update = datetime.fromisoformat(data.get("last_updated"))
        serializer = this_serializer_class_type(data=data)
        self_id = data.get("id", None)


        #Get all foreign keys referenced by this item
        all_referenced_fks = serializer.get_referenced_objects()
        self_references = []
        if recursively_update:
            for (model, referenced_id, fieldname) in all_referenced_fks:
                if str(referenced_id) == self_id:
                    self_references.append((model, referenced_id, fieldname))
                    continue #Self-reference
                this_serializer_class_type.handle_fk(model, referenced_id, from_ip, recursively_update=recursively_update)
        
        else:
            for (model, referenced_id, fieldname) in all_referenced_fks:
                if str(referenced_id) == self_id:
                    self_references.append((model, referenced_id, fieldname))
                    continue #Self reference
                if not model.objects.filter(id=referenced_id).exists():
                    this_serializer_class_type.handle_fk(model, referenced_id, from_ip, recursively_update=recursively_update)

        #Remove self-referencing foreign keys from the data
        for (_, _, fieldname) in self_references:
            data.pop(fieldname)

        data.pop("id")

        #re-make it with data stripped of self refferencing foreign keys
        serializer = this_serializer_class_type(data=data)

        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        many_to_many = []
        for (key, value) in data.items():
            if type(value) is list:
                many_to_many.append((key, value))
        for (key, _) in many_to_many:
            validated_data.pop(key)

        #kwargs are the check to see if the item exists, defaults are the values to use to create it if it doesnt
        #https://stackoverflow.com/a/50916413/7183662

        this_item = this_serializer_class_type.Meta.model.objects.filter(id=self_id)
        if this_item.exists():
            if remote_last_update <= this_item.first().last_updated:
                return this_item.first() #Item is already up to date


        created_item, created = this_serializer_class_type.Meta.model.objects.update_or_create(
            id = self_id, defaults = validated_data
        )

        did_extra_change = False

        if len(self_references) > 0:
            did_extra_change = True
            for (_, _, fieldname) in self_references:
                setattr(created_item, fieldname, created_item)

        for (field, value) in many_to_many:
            did_extra_change = True
            getattr(created_item, field).set(value)

        if did_extra_change:
            created_item.save()

        return created_item

    @classmethod
    def download_or_update_from_remote_site(this_serializer_class_type, id: uuid.UUID, from_ip: str, recursively_update = False):
        """Attempts to download/update a model instance for this serializer from a remote peer using an ip.

        Will recursively download all instances of other models this item is dependent on.
        
        :param id A UUID id
        :param from_ip The ip to download the instance from
        :param recursively_update Set to True if all instances this item depends on need to be updated. 
        Leave empty or false to only download if there isnt already a copy of it on this server. 
        Provides single-level protection against circular references (only against direct foreign key to self).
        Ensure no circular foreign key references are made in the serializers (or models)."""
        own_views = ViewContainerRegistry.get(this_serializer_class_type.Meta.model)

        url = own_views.get_detail_url(id, from_ip)
        data = HttpUtil().get_json_from_remote(url)

        return this_serializer_class_type.create_or_update_from_remote_data(
            data, 
            from_ip, 
            recursively_update=recursively_update)

    @staticmethod
    def _try_get_single_id(model: RemoteModel, data: dict, fieldname: str):
        """Tries to parse data to a uuid. Returns a tuple of the model, parsed id and the fieldname.
        
        Will ignore if the data is a dictionary as this indicates it should be handled by nested serializer fields in the serialiser child class."""
        t = type(data)
        if t is dict:
            return []#Item (probably) has custom serialiser as field, which will handle it or throw if it is wrong
        if t is type(None):
            return []#Nullable field
        if t is not str:
            raise ValidationError("UUID field is not a string")
        try:
            id = uuid.UUID(data)
            return [(model, id, fieldname)]
        except:
            raise ValidationError("Could not parse UUID to actual UUID object")

    def get_referenced_objects(self) -> List[Tuple[type, uuid.UUID]]:
        """Returns a list of all referenced foreign keys in the initial data.

        Returns list of tuples of (model, id, fieldname)."""
        data = self.initial_data
        if data is None:
            raise Exception("No data available to validate, did you pass data=? to the serialiser in its constructor?")

        referenced_foreign_keys = []
        for field in self.Meta.model._meta.get_fields():
            if field.is_relation:
                if field.many_to_many:
                    if field.name not in data.keys():
                        continue #Some foreign keys might not be synched, they will be validated for existance in the validation method of the serializer itself if needed
                    related_objects = data.get(field.name)
                    if type(related_objects) is not list:
                        raise serializers.ValidationError(f"Field {field.name} must be a list of uuid primary keys")
                    for obj_id in related_objects:
                        referenced_foreign_keys = referenced_foreign_keys + AbstractRemoteSerializer._try_get_single_id(field.related_model, obj_id, field.name)

                elif field.many_to_one or field.one_to_one:
                    if field.name not in data.keys():
                        continue #Some foreign keys might not be synched, they will be validated for existance in the validation method of the serializer itself if needed
                    related_object_id = data.get(field.name)
                    referenced_foreign_keys = referenced_foreign_keys + AbstractRemoteSerializer._try_get_single_id(field.related_model, related_object_id, field.name)
        return referenced_foreign_keys

    @classmethod
    def handle_fk(cls, model, fk, from_ip, recursively_update=False):
        """Handles updating/creating of fks that are references so that the object can be fully downloaded including dependencies.

        Handles models with an associated Abstract Remote Serializer automatically.
        
        Override to add/change handling of refferenced foreign keys, such as models without an abstract remote serializer associated with them."""
        SerializerRegistry.get(model).download_or_update_from_remote_site(fk, from_ip, recursively_update = recursively_update)

    class Meta:
        abstract = True

