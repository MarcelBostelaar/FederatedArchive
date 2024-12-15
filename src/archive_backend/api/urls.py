from django.http import HttpResponse
from django.urls import path

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

indexHTML = "".join([htmlPrintViewsetlinks(view) for view in views])

index = lambda _: HttpResponse(indexHTML)

urlpatterns = flatten([view.paths for view in views]) + [path(api_subpath, index, name="index"),]

