from .abstract_remote_serializer import SerializerRegistry
from .serializers import (
    RemotePeerSerializer, 
    LanguageSerializer, 
    FileFormatSerializer, 
    AuthorSerializer, 
    AuthorDescriptionTranslationSerializer, 
    AbstractDocumentSerializer, 
    AbstractDocumentDescriptionTranslationSerializer, 
    EditionSerializer, 
    RevisionSerializer, 
    ArchiveFileSerializer)
from .urls import urlpatterns