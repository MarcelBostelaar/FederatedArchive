import warnings
from django.db import IntegrityError, models
from archive_backend.constants import *
from archive_backend.jobs.util import pkStringList
from archive_backend.models.generation_config import GenerationConfig
from .util_abstract_models import RemoteModel
from .author_models import Author
from .abstract_document_models import AbstractDocument
from .language import Language
from model_utils import FieldTracker

class Edition(RemoteModel):
    """An edition is a concrete form of an abstract document. A specific printing, a specific digital edition or layout, a specific file format, with a specific language
    It can have additional authors (such as translators, preface writers, etc). It represents the whole history of this document, 
    so any textual corrections in the transcription, for example, are not grounds for a new "edition",
    unless explicit differentiation is desired such as archiving several historic prints of the same general book."""
    edition_of = models.ForeignKey(AbstractDocument, on_delete=models.CASCADE, related_name="editions")
    publication_date = models.DateField(blank=True, null=True)
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    additional_authors = models.ManyToManyField(Author, blank=True)
    
    title = models.CharField(max_length=titleLength)
    description = models.CharField(max_length=descriptionLength)

    generation_config = models.ForeignKey(GenerationConfig, on_delete=models.SET_NULL, null=True, blank=True)
    actively_generated_from = models.ForeignKey("Edition", related_name="generation_dependencies", on_delete=models.SET_NULL, null=True, blank=True)
    field_tracker = FieldTracker(fields=["actively_generated_from", "generation_config"])

    def __str__(self) -> str:
        return self.title + " - (" + self.language.iso_639_code + ")"
