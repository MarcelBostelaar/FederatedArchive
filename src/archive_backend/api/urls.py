
from django.http import HttpResponse
from django.urls import path

from archive_backend.utils.small import flatten
from .apiviews import *

def htmlPrintViewsetlinks(ViewsDataContainer):
    base =  f"""
    <h1>{ViewsDataContainer.model_name}</h1>
    <ul>
    <li><a href="/{ViewsDataContainer.list_url}">List view</a></li>
    <li><a href="/{ViewsDataContainer.detail_url}yourpkhere">Detail view</a></li>
    """
    if hasattr(ViewsDataContainer, "alias_url"):
        base += f"""<li><a href="/{ViewsDataContainer.alias_url}">Aliases</a></li>"""
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

