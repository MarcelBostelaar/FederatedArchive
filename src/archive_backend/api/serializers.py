import uuid
from rest_framework import serializers
from archive_backend.models import *

class DummySerializer(serializers.ModelSerializer):
    def get_non_existant_referenced_objects(self):
        """Checks if all refferenced foreign key in the passed in data exist in the database.
        
        Does not work when custom validators for specific fields are implemented, as it checks the initial data directly."""
        data = self.initial_data
        if data is None:
            raise Exception("No data available to validate, did you pass data=? to the serialiser in its constructor?")

        missing = []
        for field in self.Meta.model._meta.get_fields():
            if field.is_relation:
                if field.many_to_many:
                    if field.name not in data.keys():
                        raise serializers.ValidationError(f"Field {field.name} is required")
                    related_objects = data.get(field.name)
                    if type(related_objects) is not list:
                        raise serializers.ValidationError(f"Field {field.name} must be a list of uuid primary keys")
                    for obj_id in related_objects:
                        id = uuid.UUID(obj_id)
                        if not field.related_model.objects.filter(pk=id).exists():
                            missing.append((field.related_model, id))

                elif field.many_to_one or field.one_to_one:
                    if field.name not in data.keys():
                        raise serializers.ValidationError(f"Field {field.name} is required")
                    related_object_id = data.get(field.name)
                    id = uuid.UUID(related_object_id)
                    if not field.related_model.objects.filter(pk=id).exists():
                        missing.append((field.related_model, id))
        return missing


    class Meta:
        abstract = True

class RemotePeerSerializer(serializers.ModelSerializer):
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
    class Meta:
        model = Revision
        exclude = ["generated_from"]

class ArchiveFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArchiveFile
        exclude = ["file"]
