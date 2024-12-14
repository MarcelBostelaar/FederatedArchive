from typing import List, Tuple
import uuid
import requests
from rest_framework import serializers
from archive_backend.models import *
from archive_backend.utils import registry
from .viewset_data_containers import ViewContainerRegistry

SerializerRegistry = registry()

class AbstractRemoteSerializer(serializers.ModelSerializer):
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not hasattr(cls.Meta, "abstract") or not cls.Meta.abstract:
            SerializerRegistry.register(cls.Meta.model, cls)

    @classmethod
    def download_from_remote_site(this_serializer_class_type, id, from_ip):
        own_views = ViewContainerRegistry.get(this_serializer_class_type.Meta.model)

        url = from_ip + "/" + own_views.detail_url + str(id) + "?format=json"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        serializer = this_serializer_class_type(data=data)

        non_existent_objects = serializer.get_non_existant_referenced_objects()

        # If any return, run their download first
        for (model, id) in non_existent_objects:
            result = SerializerRegistry.get(model).download_from_remote_site(id, from_ip)
            if result is None:
                raise serializers.ValidationError(f"Failed to download {model.__name__} with id {id} from {from_ip}")

        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        created_item, created = this_serializer_class_type.Meta.model.objects.update_or_create(
            id=id, **validated_data
        )

        return created_item

    def get_non_existant_referenced_objects(self) -> List[Tuple[type, uuid.UUID]]:
        """Checks if all refferenced foreign key in the passed in data exist in the database.

        Returns list of tuples of (model, id) of missing objects.
        
        Does not work when custom validators for specific fields are implemented, as it checks the initial data directly."""
        data = self.initial_data
        if data is None:
            raise Exception("No data available to validate, did you pass data=? to the serialiser in its constructor?")

        missing = []
        for field in self.Meta.model._meta.get_fields():
            if field.is_relation:
                if field.many_to_many:
                    if field.name not in data.keys():
                        continue #Some foreign keys might not be synched, they will be validated for existance in the validation method of the serializer itself if needed
                    related_objects = data.get(field.name)
                    if type(related_objects) is not list:
                        raise serializers.ValidationError(f"Field {field.name} must be a list of uuid primary keys")
                    for obj_id in related_objects:
                        id = uuid.UUID(obj_id)
                        if not field.related_model.objects.filter(pk=id).exists():
                            missing.append((field.related_model, id))

                elif field.many_to_one or field.one_to_one:
                    if field.name not in data.keys():
                        continue #Some foreign keys might not be synched, they will be validated for existance in the validation method of the serializer itself if needed
                    related_object_id = data.get(field.name)
                    id = uuid.UUID(related_object_id)
                    if not field.related_model.objects.filter(pk=id).exists():
                        missing.append((field.related_model, id))
        return missing


    class Meta:
        abstract = True

class RemotePeerSerializer(AbstractRemoteSerializer):
    class Meta:
        model = RemotePeer
        exclude = ["is_this_site", "mirror_files", "last_checkin"]

class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        exclude = ["alias_identifier"]

class FileFormatSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileFormat
        exclude = ["alias_identifier"]

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        exclude = ["alias_identifier"]

class AuthorDescriptionTranslationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthorDescriptionTranslation
        fields = "__all__"

class AbstractDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AbstractDocument
        exclude = ["alias_identifier"]

class AbstractDocumentDescriptionTranslationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AbstractDocumentDescriptionTranslation
        fields = "__all__"

class EditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Edition
        exclude = ["actively_generated_from", "generation_config"]

class RevisionSerializer(serializers.ModelSerializer):

    def validate_status(self, value):
        """Validate remote status"""
        #TODO implement and change validated status to be appropriate for this (ie if it read "job scheduled" from remote, it should be "remote job scheduled" in this database)
        raise NotImplementedError()

    class Meta:
        model = Revision
        exclude = ["generated_from"]

class ArchiveFileSerializer(serializers.ModelSerializer):
    def validate_file(self, value):
        #TODO
        raise NotImplementedError()

    class Meta:
        model = ArchiveFile
        exclude = ["file"]
