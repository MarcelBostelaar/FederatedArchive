from rest_framework import serializers
from archive_backend.models import *

class SerializerSet:
    def __init__(self, simple = None, alias = None):
        self.simple = simple
        self.alias = alias
    simple = None
    alias = None

def makeSimpleRemoteSerializer(cls):
    class _RemotableSerializer(serializers.ModelSerializer):
        class Meta:
            model = cls
            fields = '__all__'
    return SerializerSet(simple = _RemotableSerializer, alias = None)

def makeAliasSerializers(cls):
    name = cls.__name__
    throughname = name + "AliasThrough"
    class _AliasableSerializer(serializers.ModelSerializer):
        class Meta:
            model = cls
            exclude = ["_alias_identifier"]
    class _ThoughSerializer(serializers.ModelSerializer):
        class Meta:
            model = archiveAppConfig.get_model(throughname)
            fields = '__all__'
    return SerializerSet(simple = _AliasableSerializer, alias = _ThoughSerializer)

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