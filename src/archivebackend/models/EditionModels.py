import datetime
import warnings
from django import forms
from django.db import models
from archivebackend.constants import *
from .modelsAbstract import RemoteModel
from .AuthorModels import Author
from .AbstractDocumentModels import AbstractDocument
from .Language import Language
from archivebackend.utils import flatten

class existanceType(models.IntegerChoices):
    """Describes how the edition exists on this server"""
    LOCAL = 0 # Basic local files
    AUTOGENERATED = 1 # It is auto generated on our server from a different file.
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

    #precalculated to quickly serve users and reduce load in backend
    file_url = models.CharField(max_length=maxFileNameLength, blank=True)
    last_file_update = models.DateTimeField(blank=True, default=datetime.datetime(1970, 1, 1, 1, 00))

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
        if(self._existance_type == newState):
            return
        if(newState == existanceType.LOCAL):
            self._existance_type = existanceType.LOCAL
            return
        elif(newState == existanceType.AUTOGENERATED):
            raise ValueError("Cannot set existance type to autogenerated from another state.")
        elif(newState == existanceType.REMOTE):
            if(self._existance_type == existanceType.MIRROREDREMOTE):
                self._existance_type = existanceType.REMOTE
                return
            else:
                raise ValueError("Cannot set existance type to remote from local of autogenerated.")
        elif(newState == existanceType.MIRROREDREMOTE):
            if(self._existance_type == existanceType.REMOTE):
                self._existance_type = existanceType.MIRROREDREMOTE
                return
            else:
                raise ValueError("Cannot set existance type to mirrored remote from local of autogenerated.")
        raise NotImplementedError("Unknown existance type: " + str(newState))

    exclude_fields_from_synch = ["existance_type"]
    
    def save(self, *args, **kwargs):
        #TODO disallow making existance type go from anything else to Local, local forks must be explicitly made as new instances.
        super(Edition, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return self.title + " - (" + self.language.iso_639_code + ")"

    def clean(self): #TODO move back to admin view, replace all admin views with a custom form to get around the admin view limitations
        """Ensure no authors are duplicated in either the original authors list or the additional authors list"""
        editionAuthors = list(self.edition_of.authors.all())
        additionalAuthors = list(self.additional_authors.all())
        originalAuthorsAliases = set(flatten([x.allAliases() for x in editionAuthors]))
        additionalAuthorsAliases = flatten([x.allAliases() for x in additionalAuthors])
        # If the set of aliases is the same length as the list, then there are no mutually aliased items in the list
        isUnique = len(set(additionalAuthorsAliases)) == len(additionalAuthorsAliases)
        InOriginal = any([extraAuthor in originalAuthorsAliases for extraAuthor in additionalAuthors])
        if not isUnique:
            duplicates = [author for author in additionalAuthors if additionalAuthorsAliases.count(author) > 1]
            raise forms.ValidationError("Some authors are duplicated in the additional authors list: " + ", ".join([author.fallback_name for author in duplicates]))
        if InOriginal:
            raise forms.ValidationError("Some authors are already in the original authors list: " + ", ".join([author.fallback_name for author in additionalAuthors if author in originalAuthorsAliases]))
