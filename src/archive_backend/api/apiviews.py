
from .viewset_data_containers import AliasViewDataContainer, RemoteViewDataContainer
from . import serializers as s

api_subpath = "api/"

RemotePeerViews = RemoteViewDataContainer(s.RemotePeerSerializer, api_subpath)
LanguageViews = AliasViewDataContainer(s.LanguageSerializer, api_subpath)
FileFormatViews = AliasViewDataContainer(s.FileFormatSerializer, api_subpath)
AuthorViews = AliasViewDataContainer(s.AuthorSerializer, api_subpath)
AuthorDescriptionTranslationViews = RemoteViewDataContainer(s.AuthorDescriptionTranslationSerializer, api_subpath)
AbstractDocumentViews = AliasViewDataContainer(s.AbstractDocumentSerializer, api_subpath)
AbstractDocumentDescriptionTranslationViews = RemoteViewDataContainer(s.AbstractDocumentDescriptionTranslationSerializer, api_subpath)
EditionViews = RemoteViewDataContainer(s.EditionSerializer, api_subpath)
RevisionViews = RemoteViewDataContainer(s.RevisionSerializer, api_subpath)
ArchiveFileViews = RemoteViewDataContainer(s.ArchiveFileSerializer, api_subpath)

