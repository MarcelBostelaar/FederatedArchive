from rest_framework.generics import RetrieveAPIView
from rest_framework import generics

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
    return generated

def listView(cls, serializer):
    """Generates a view for listing all instances of a model."""
    class _ItemListView(generics.ListCreateAPIView):
        queryset = cls.objects.all()
        serializer_class = serializer
    return _ItemListView
