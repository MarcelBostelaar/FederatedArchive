import json
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import path

from archive_backend.api.trigger_request import trigger_revision_request
from archive_backend.models.remote_peer import RemotePeer
from archive_backend.models.revision import Revision
from archive_backend.utils.small import flatten
from .apiviews import *

def htmlPrintViewsetlinks(ViewsDataContainer: RemoteViewDataContainer | AliasViewDataContainer):
    base =  f"""
    <h1>{ViewsDataContainer.model_name}</h1>
    <ul>
    <li><a href="{ViewsDataContainer.get_list_url("", json_format=False)}">List view</a></li>
    <li><a href="{ViewsDataContainer.get_detail_url("", "", json_format=False)}">Detail view</a></li>
    """
    if hasattr(ViewsDataContainer, "alias_url"):
        base += f"""<li><a href="{ViewsDataContainer.get_alias_url("", json_format=False)}">Aliases</a></li>"""
    return base + "</ul>"

views = [
    RemotePeerViews,
    LanguageViews,
    FileFormatViews,
    AuthorViews,
    AuthorDescriptionTranslationViews,
    AbstractDocumentViews,
    AbstractDocumentDescriptionTranslationViews, 
    EditionViews,
    RevisionViews,
    ArchiveFileViews
]

indexHTML = "".join(["<a href='./peer_self'>This peer api point</a>"] + [htmlPrintViewsetlinks(view) for view in views])

index = lambda _: HttpResponse(indexHTML)

self_remote = lambda _: redirect(RemotePeerViews.get_detail_url(RemotePeer.getLocalSite().id), permanent=True)

trigger_request_base = api_subpath + "/revision/trigger/"
def getTriggerRequestUrl(revision: Revision):
    return trigger_request_base + str(revision.id)

urlpatterns = flatten([view.paths for view in views]) + [
    path(api_subpath, index, name="index"),
    path(api_subpath + "peer_self", self_remote, name="peer_self"),
    path(trigger_revision_request + "<uuid:pk>", trigger_revision_request, name="trigger_revision_request"),
    ]

