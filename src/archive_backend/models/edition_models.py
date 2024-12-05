import warnings
from django.db import IntegrityError, models
from archive_backend.constants import *
from archive_backend.jobs.util import pkStringList
from archive_backend.models.generation_config import GenerationConfig
from .util_abstract_models import RemoteModel
from .author_models import Author
from .abstract_document_models import AbstractDocument
from .language import Language
from django_q.tasks import async_task

class existanceType(models.IntegerChoices):
    """Describes how the edition exists on this server"""
    LOCAL = 0 # Basic local files
    GENERATED = 1 # It is generated on our server from a different file.
    REMOTE = 2 # It exists on a remote server, but isnt mirrored. Just links to the remote file. (saves storage)
    MIRROREDREMOTE = 3 # It exists on a remote server, and is copied locally by this instance for reliability/speed/archival purposes.

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
    _existance_type = models.IntegerField(existanceType, default=existanceType.LOCAL, blank=True)

    generation_config = models.ForeignKey(GenerationConfig, on_delete=models.SET_NULL, null=True, blank=True)
    actively_generated_from = models.ForeignKey("Edition", related_name="generation_dependencies", on_delete=models.SET_NULL, null=True, blank=True)

    @property
    def existance_type(self):
        return self._existance_type
    
    @existance_type.setter
    def existance_type(self, newState):
        """Prevents transition of illegal states. See 'signals' in documentation for more information."""
        # TODO remove after testing
        warnings.warn("State machine for existance type is disabled")
        self._existance_type = newState
        return
        if self._existance_type == newState:
            return
        if self._existance_type == None:
            self._existance_type = newState
            return
        match [self._existance_type, newState]:
            case [existanceType.LOCAL, existanceType.GENERATED]:
                if self.autogeneration is not None:
                    self._existance_type = newState
                    return
                raise ValueError("An auto generation configuration for this item has not been set, add it first.")
            case [existanceType.GENERATED, existanceType.LOCAL]:
                self._existance_type = newState
                return
            case [existanceType.REMOTE, existanceType.MIRROREDREMOTE]:
                self._existance_type = newState
                return
            case [existanceType.MIRROREDREMOTE, existanceType.REMOTE]:
                self._existance_type = newState
                return
            case _:
                raise NotImplementedError("Illegal existance type state transtion from {self._existance_type} to {newState}")

    def __str__(self) -> str:
        return self.title + " - (" + self.language.iso_639_code + ")"
