from django import forms
from django.db import models
from archive_backend.constants import *
from .language import Language
from .author_models import Author
from .util_abstract_models import AliasableModel, RemoteModel

class AbstractDocument(AliasableModel("AbstractDocument")):
    """Represents an abstract document. For example, 'the first Harry Potter book', regardless of language, edition, print, etc.
    """
    original_publication_date = models.DateField(blank=True, null=True)
    authors = models.ManyToManyField(Author, blank=True)
    fallback_name = models.CharField(max_length=maxFileNameLength)

    def __str__(self) -> str:
        return self.fallback_name

class AbstractDocumentDescriptionTranslation(RemoteModel):
    """Provides functionality for adding titles and descriptions of abstract documents in multiple languages"""
    describes = models.ForeignKey(AbstractDocument, on_delete=models.CASCADE, related_name="descriptions")
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    translation = models.CharField(max_length=titleLength)
    description = models.CharField(max_length=descriptionLength, blank=True)

    def __str__(self) -> str:
        return self.translation + " - (" + self.language.iso_639_code + ")"
