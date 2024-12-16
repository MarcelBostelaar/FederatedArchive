from datetime import datetime
from typing import override
from uuid import UUID
from .registries import *
from .viewset_data_containers import AliasViewDataContainer, RemoteViewDataContainer
from . import serializers as s

api_subpath = "api/"

class RevisionViewsClass(RemoteViewDataContainer):
    """Custom views data container class to add extra url parameters for the list views"""
    def __init__(self, model_serializer, subpath="", RemoteViewset=None):
        super().__init__(model_serializer, subpath, RemoteViewset)

    @override
    def get_list_url(self, on_site = "", json_format = True, updated_after: datetime = None, related_edition: UUID = None, latest_only: bool = False):
        return self._generate_url(on_site, self._list_url, 
                                  updated_after=updated_after.isoformat() if updated_after else "", 
                                  format="json" if json_format else "",
                                  related_edition=related_edition if related_edition else "",
                                  latest_only=latest_only if latest_only else "")

RemotePeerViews = RemoteViewDataContainer(s.RemotePeerSerializer, api_subpath)
LanguageViews = AliasViewDataContainer(s.LanguageSerializer, api_subpath)
FileFormatViews = AliasViewDataContainer(s.FileFormatSerializer, api_subpath)
AuthorViews = AliasViewDataContainer(s.AuthorSerializer, api_subpath)
AuthorDescriptionTranslationViews = RemoteViewDataContainer(s.AuthorDescriptionTranslationSerializer, api_subpath)
AbstractDocumentViews = AliasViewDataContainer(s.AbstractDocumentSerializer, api_subpath)
AbstractDocumentDescriptionTranslationViews = RemoteViewDataContainer(s.AbstractDocumentDescriptionTranslationSerializer, api_subpath)
EditionViews = RemoteViewDataContainer(s.EditionSerializer, api_subpath)
RevisionViews = RevisionViewsClass(s.RevisionSerializer, api_subpath)
ArchiveFileViews = RemoteViewDataContainer(s.ArchiveFileSerializer, api_subpath)

