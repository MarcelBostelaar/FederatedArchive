from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import path

from .trigger_request import trigger_revision_request_endpoint, trigger_request_base
from archive_backend.models.remote_peer import RemotePeer
from archive_backend.utils.small import flatten
from .apiviews import *
from archive_backend.models.archive_file import ArchiveFile

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

indexHTML = "".join(["<a href='./peer_self'>This peer api point</a>"] + 
                    [htmlPrintViewsetlinks(view) for view in views] + 
                    ["""<h1>Files</h1>
                     <ul>
                     <li><a href='./file/uuid'>File endpoint</a></li>
                     </ul>"""])

index = lambda _: HttpResponse(indexHTML)

self_remote = lambda _: redirect(RemotePeerViews.get_detail_url(RemotePeer.getLocalSite().id), permanent=True)

def file_by_id(request, file_id):
    """Redirects to the file url of the given file id"""
    try:
        archive_file = ArchiveFile.objects.get(id=file_id)
        if archive_file.belongs_to.status == RevisionStatus.ONDISKPUBLISHED:
            return redirect(archive_file.file.url, permanent=False)
        if request.user.is_authenticated and request.user.is_staff:
            return HttpResponse("Unauthorized", status=401)
        return redirect(archive_file.file_url, permanent=False)
    except ArchiveFile.DoesNotExist:
        return HttpResponse("File not found", status=404)

urlpatterns = flatten([view.paths for view in views]) + [
    path(api_subpath, index, name="index"),
    path(api_subpath + "peer_self", self_remote, name="peer_self"),
    path(trigger_request_base + "<uuid:pk>", trigger_revision_request_endpoint, name="trigger_revision_request"),
    path(api_subpath + "file/<uuid:file_id>", file_by_id, name="file_by_id"),
    ]

