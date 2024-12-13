from rest_framework import serializers
from archive_backend.models import *

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
