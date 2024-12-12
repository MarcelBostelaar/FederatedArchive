from rest_framework.viewsets import ReadOnlyModelViewSet

from .serializers import generatedSerializers
from archive_backend.models.author_models import Author

class GenericViewset(ReadOnlyModelViewSet):
    queryset = Author.objects.all()
    serializer_class = generatedSerializers[Author].main_serializer

    #if has alias, add alias subviewset and add that to the urls

    #override retrieve method to handle filtering between dates

    @property
    def urls(self):
        return super().urls + []#Add alias here if needed


