from datetime import datetime
from typing import override
from uuid import UUID

from archive_backend import models
from .registries import *
from .viewset_data_containers import AliasViewDataContainer, RemoteViewDataContainer, RemoteViewsetFactory
from . import serializers as s

api_subpath = "api/"

class RevisionViewset(RemoteViewsetFactory(models.Revision)):
    @override
    def get_queryset(self):
        the_set = super().get_queryset()
        rel_edition = self.request.query_params.get('related_edition', None)
        if rel_edition:
            the_set = the_set.filter(belongs_to_id = rel_edition)

        backsups = self.request.query_params.get('backsups_only', False)
        if backsups:
            the_set = the_set.filter(is_backup = True)

        latest = self.request.query_params.get('latest_only', False)
        if latest:
            the_set = the_set.order_by("-date")[:1]
        return the_set

class RevisionViewsContainerClass(RemoteViewDataContainer):
    """Custom views data container class to add extra url parameters for the list views"""
    def __init__(self, model_serializer, subpath="", RemoteViewset=RevisionViewset):
        super().__init__(model_serializer, subpath, RemoteViewset)

    @override
    def get_list_url(self, 
                     on_site = "", 
                     json_format = True, 
                     updated_after: datetime = None, 
                     related_edition: UUID = None, 
                     latest_only: bool = False,
                     backups_only: bool = False):
        return self._generate_url(on_site, self._list_url, 
                                  updated_after=updated_after.isoformat() if updated_after else "", 
                                  format="json" if json_format else "",
                                  related_edition=str(related_edition) if related_edition else "",
                                  latest_only=str(latest_only) if latest_only else "",
                                  backups_only=str(backups_only) if backups_only else "")
    
class ArchiveFileViewset(RemoteViewsetFactory(models.ArchiveFile)):
    @override
    def get_queryset(self):
        the_set = super().get_queryset()
        rel_revision = self.request.query_params.get('related_revision', None)
        if rel_revision:
            the_set = the_set.filter(belongs_to_id = rel_revision)
        return the_set
    
    
class ArchiveFileViewsContainerClass(RemoteViewDataContainer):
    """Custom views data container class to add extra url parameters for the list views"""
    def __init__(self, model_serializer, subpath="", RemoteViewset=ArchiveFileViewset):
        super().__init__(model_serializer, subpath, RemoteViewset)

    @override
    def get_list_url(self, on_site = "", json_format = True, updated_after: datetime = None, related_revision: UUID = None):
        return self._generate_url(on_site, self._list_url, 
                                  updated_after=updated_after.isoformat() if updated_after else "", 
                                  format="json" if json_format else "",
                                  related_revision=str(related_revision) if related_revision else "")
    
class RemotePeerViewset(RemoteViewsetFactory(models.RemotePeer)):
    @override
    def get_queryset(self):
        the_set = super().get_queryset()
        only_self = self.request.query_params.get('only_self', False)
        if only_self:
            the_set = the_set.filter(is_this_site = True)
        return the_set

class RemotePeerViewsContrainerClass(RemoteViewDataContainer):
    """Custom views data container class to add extra url parameters for the list views"""
    def __init__(self, model_serializer, subpath="", RemoteViewset=RemotePeerViewset):
        super().__init__(model_serializer, subpath, RemoteViewset)
    
    @override
    def get_list_url(self, on_site = "", json_format = True, updated_after: datetime = None, only_self: bool = False):
        return self._generate_url(on_site, self._list_url, 
                                  updated_after=updated_after.isoformat() if updated_after else "", 
                                  format="json" if json_format else "",
                                  only_self=str(only_self) if only_self else "")

RemotePeerViews = RemotePeerViewsContrainerClass(s.RemotePeerSerializer, api_subpath)
LanguageViews = AliasViewDataContainer(s.LanguageSerializer, api_subpath)
FileFormatViews = AliasViewDataContainer(s.FileFormatSerializer, api_subpath)
AuthorViews = AliasViewDataContainer(s.AuthorSerializer, api_subpath)
AuthorDescriptionTranslationViews = RemoteViewDataContainer(s.AuthorDescriptionTranslationSerializer, api_subpath)
AbstractDocumentViews = AliasViewDataContainer(s.AbstractDocumentSerializer, api_subpath)
AbstractDocumentDescriptionTranslationViews = RemoteViewDataContainer(s.AbstractDocumentDescriptionTranslationSerializer, api_subpath)
EditionViews = RemoteViewDataContainer(s.EditionSerializer, api_subpath)
RevisionViews = RevisionViewsContainerClass(s.RevisionSerializer, api_subpath)
ArchiveFileViews = ArchiveFileViewsContainerClass(s.ArchiveFileSerializer, api_subpath)

