from typing import List, Tuple
import uuid
from django.forms import ValidationError
import requests
from rest_framework import serializers
from archive_backend.models import RemoteModel
from archive_backend.utils import registry
from .viewset_data_containers import ViewContainerRegistry

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
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not hasattr(cls.Meta, "abstract") or not cls.Meta.abstract:
            SerializerRegistry.register(cls.Meta.model, cls) #Register all subclasses that arent abstract to the registry

    @classmethod
    def create_or_update_from_remote_date(this_serializer_class_type, data: dict, from_ip: str, recursively_update = False):
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
        serializer = this_serializer_class_type(data=data)

        all_referenced_fks = serializer.get_referenced_objects()
        if recursively_update:
            for (model, referenced_id) in all_referenced_fks:
                if referenced_id == id:
                    continue #Self-reference, for remote_models, skip update
                SerializerRegistry.get(model).download_or_update_from_remote_site(referenced_id, from_ip, recursively_update = True)
        
        else:
            for (model, referenced_id) in all_referenced_fks:
                if not model.objects.filter(id=referenced_id).exists():
                    SerializerRegistry.get(model).download_or_update_from_remote_site(referenced_id, from_ip)

        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        created_item, created = this_serializer_class_type.Meta.model.objects.update_or_create(
            id=id, **validated_data
        )

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
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        return this_serializer_class_type.create_or_update_from_remote_date(
            data, 
            from_ip, 
            recursively_update=recursively_update)
        

    @staticmethod
    def _try_get_single_id(model: RemoteModel, data: dict):
        """Tries to parse data to a uuid. Returns a tuple of the model and the parsed id.
        
        Will ignore if the data is a dictionary as this indicates it should be handled by nested serializer fields in the serialiser child class."""
        t = type(data)
        if t is dict:
            return []#Item (probably) has custom serialiser as field, which will handle it or throw if it is wrong
        if t is not str:
            raise ValidationError("UUID field is not a string")
        try:
            id = uuid.UUID(data)
            return [(model, id)]
        except:
            raise ValidationError("Could not parse UUID to actual UUID object")

    def get_referenced_objects(self) -> List[Tuple[type, uuid.UUID]]:
        """Returns a list of all referenced foreign keys in the initial data.

        Returns list of tuples of (model, id)."""
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
                        referenced_foreign_keys = referenced_foreign_keys + AbstractRemoteSerializer._try_get_single_id(field.related_model, obj_id)

                elif field.many_to_one or field.one_to_one:
                    if field.name not in data.keys():
                        continue #Some foreign keys might not be synched, they will be validated for existance in the validation method of the serializer itself if needed
                    related_object_id = data.get(field.name)
                    referenced_foreign_keys = referenced_foreign_keys + AbstractRemoteSerializer._try_get_single_id(field.related_model, related_object_id)
        return referenced_foreign_keys

    class Meta:
        abstract = True

#Used to programmatically find a serializer for a remote model using the original model class as a key
SerializerRegistry = registry[RemoteModel, AbstractRemoteSerializer](registry_name_for_debugging="Serializers")
