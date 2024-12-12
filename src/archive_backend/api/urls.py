from django.http import HttpResponse
from django.urls import  path
from archive_backend.api.view_set import GenericViewset
from archive_backend.constants import api_subpath
from rest_framework import viewsets
from rest_framework.routers import DefaultRouter

from archive_backend.models.author_models import Author

from .serializers import generatedSerializers

def itemDisplay(item):
    alias = ""
    if item.alias_list is not None:
        alias = f"""<li><a href="/{item.urlForAliasList()}">Aliases:&emsp;{item.urlForAliasList()}</a></li>"""

    return f"""
    <h2>{item.itemName()}</h2>
    <ul>
        <li><a href="/{item.urlForCoreList()}">List:&emsp;{item.urlForCoreList()}</a></li>
        <li><a href="/{item.urlForCoreItem("yourpkhere")}">Individual:&emsp;{item.urlForCoreItem("yourpkhere")}</a></li>
        {alias}
    </ul>
"""

def apiIndex(request):
    x = "".join([itemDisplay(x) for x in generatedSerializers.values()])

    return HttpResponse("<h1>API Index</h1>" + x)


router = DefaultRouter()
router.register(r'authors', GenericViewset, basename='author')
urlpatterns = router.urls
print(urlpatterns)
# urlpatterns = ([path(api_subpath, apiIndex, name="apiindex")]
                #    + [x.main_single_path for x in generatedSerializers.values()] 
                #    + [x.main_list for x in generatedSerializers.values()]
                #    + [x.alias_list for x in generatedSerializers.values() if x.alias_list is not None]
                #    )