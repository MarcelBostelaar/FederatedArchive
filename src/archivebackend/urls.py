from django.urls import path, include
from rest_framework import routers

from archivebackend import views
from archivebackend.api.apiviews import uuidRetrieve
from archivebackend.api.modelSerializers.Revision import RemoteSerializer, RevisionSerializer, TestSerializer

def uuidPath(serializer):
    """Generates an api endpoint for a given serializer, using the model name (which uses a uuid as a pk) as the endpoint."""
    cls = serializer.Meta.model
    return path("api/" + cls.__name__.lower() + '/<uuid:pk>/', uuidRetrieve(cls, serializer).as_view(), name=cls.__name__.lower())

uuidretrieves = [
    TestSerializer,
    RevisionSerializer
]

urlpatterns = [
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path("", views.index, name="index"),
] + list(map(uuidPath, uuidretrieves))