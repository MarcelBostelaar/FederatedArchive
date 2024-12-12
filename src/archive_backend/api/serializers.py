from django.urls import path
from rest_framework import serializers
from archive_backend.api.apiviews import listView, uuidRetrieve
from archive_backend.models import *
from archive_backend.constants import api_subpath

class SerializerSet:
    def __init__(self, main_serializer, alias_table_serializer = None):
        self.main_serializer = main_serializer
        self.alias_table_serializer = alias_table_serializer

def makeSimpleRemoteSerializer(cls):
    class _RemotableSerializer(serializers.ModelSerializer):
        class Meta:
            model = cls
            fields = '__all__'
    return SerializerSet(main_serializer = _RemotableSerializer, alias_table_serializer = None)

def makeAliasSerializers(cls):
    name = cls.__name__
    throughname = name + "AliasThrough"
    class _AliasableSerializer(serializers.ModelSerializer):
        class Meta:
            model = cls
            exclude = ["alias_identifier"]
    class _ThoughSerializer(serializers.ModelSerializer):
        class Meta:
            model = archiveAppConfig.get_model(throughname)
            fields = '__all__'
    return SerializerSet(main_serializer = _AliasableSerializer, alias_table_serializer = _ThoughSerializer)

def makeSerializer(cls):
    base = cls.__bases__[0]
    if base.__name__ == "AliasableModel_":
        return makeAliasSerializers(cls)
    if issubclass(cls, RemoteModel):
        return makeSimpleRemoteSerializer(cls)
    raise Exception("Class " + cls.__name__ + " is not a remote model or aliasable model.")

classesToSerialize = [
    RemotePeer,
    Language,
    FileFormat,
    Author,
    AuthorDescriptionTranslation,
    AbstractDocument,
    AbstractDocumentDescriptionTranslation,
    Edition,
    Revision,
    ArchiveFile
]

generatedSerializers = {cls: makeSerializer(cls) for cls in classesToSerialize}