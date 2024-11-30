from typing import Generic
from django.contrib.auth.models import Group, User
from rest_framework import permissions, viewsets
from rest_framework.generics import RetrieveAPIView
from .modelSerializers.Revision import RemoteSerializer, RevisionSerializer
from archive_backend.models import RemotePeer, Revision

def uuidRetrieve(cls, serializer):
    """Generates a RetrieveAPIView for a given model and serializer."""
    class uuidRetrieveInternal(RetrieveAPIView):
        """Retrieve a single instance of a model."""
        queryset = cls.objects.all()
        serializer_class = serializer
        lookup_field = 'pk'
    generatedName = cls.__name__ + "Retrieve"
    generated = type(generatedName, (uuidRetrieveInternal, ),
                     {"__module__" : __name__, "__qualname__" : generatedName})
    globals()[generated.__name__] = generated
    return generated
