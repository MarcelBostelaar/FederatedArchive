from django.db import models
from ArchiveBackend.constants import *
from .Language import Language
from .modelsAbstract import AliasableModel, RemoteModel

class Author(AliasableModel("Author")):
    fallback_name = models.CharField(max_length=authorLength)
    birthday = models.DateField(blank=True, null=True)

    def __str__(self) -> str:
        if self.birthday is not None:
            return self.fallback_name + " - " + str(self.birthday)
        return self.fallback_name

class AuthorDescriptionTranslation(RemoteModel):
    describes = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="descriptions")
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    translation = models.CharField(max_length=authorLength)
    description = models.CharField(max_length=descriptionLength, blank=True)

    def __str__(self) -> str:
        return self.translation + " - (" + self.language.iso_639_code + ")"
