from django.http import HttpResponse
from django.urls import include, path

from .apiviews import listView, uuidRetrieve
from .serializers import generatedSerializers

def uuidPath(serializer):
    """Generates an api endpoint for a given serializer, using the model name (which uses a uuid as a pk) as the endpoint."""
    cls = serializer.Meta.model
    return path(cls.__name__.lower() + '/<uuid:pk>/', uuidRetrieve(cls, serializer).as_view(), name=cls.__name__.lower())

def listPath(serializer):
    """Generates an list view api endpoint for a given serializer, using the model name as the endpoint."""
    cls = serializer.Meta.model
    return path(cls.__name__.lower(), listView(cls, serializer).as_view(), name=cls.__name__.lower() + "list")




singles = [uuidPath(x.simple) for x in generatedSerializers.values()]
lists = [listPath(x.simple) for x in generatedSerializers.values()] + [listPath(x.alias) for x in generatedSerializers.values() if x.alias is not None]

urlpatterns = [path("", lambda _: HttpResponse("Hello test!"), name="apiindex"),
                path("single/", include(singles)),
                path("list/", include(lists))            
                ]