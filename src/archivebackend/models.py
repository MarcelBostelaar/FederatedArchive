import datetime
import string
from django import forms
from django.db import models
from archivebackend.constants import *
from archivebackend.modelsAbstract import AliasableModel, RemoteBackupModel, RemoteModel
from archivebackend.utils import flatten

class existanceType(models.IntegerChoices):
    """Describes how the edition exists on this server"""
    LOCAL = 0 # Basic local files
    UNGENERATED = 1 # It should be generated from another file.
    GENERATING = 2 # It is currently being generated.
    AUTOGENERATED = 3 # It is auto generated on our server from a different file.
    REMOTE = 4 # It exists on a remote server, but isnt mirrored. Just links to the remote file. (saves storage)
    MIRROREDREMOTE = 5 # It exists on a remote server, and is copied locally by this instance for reliability/speed/archival purposes.

#Models

class RemotePeer(RemoteModel):
    site_name = models.CharField(max_length=titleLength)
    site_adress = models.CharField(max_length=maxFileNameLength)
    mirror_files = models.BooleanField(blank=True, default=False)
    peers_of_peer = models.BooleanField(blank=True, default=True)
    last_checkin = models.DateTimeField(blank=True, default=datetime.datetime(1970, 1, 1, 0, 0, 0, 0))
    is_this_site = models.BooleanField(blank=True, default=False)

    exclude_fields_from_synch = ["is_this_site", "last_checkin", "peers_of_peer", "mirror_files"]

    def __str__(self) -> str:
        return self.site_name + " - " + self.site_adress
    
class FileFormat(AliasableModel("FileFormat")):
    format = models.CharField(max_length=10, unique=True)
    
    def save(self, *args, **kwargs):
        parsedFormat = self.format.replace(" ", "").replace(".", "").lower()
        if not set(parsedFormat) <= set(string.ascii_lowercase + string.digits):
            raise Exception("File format can only contain letters and numbers")
        super(FileFormat, self).save(*args, **kwargs)
    
    def __str__(self) -> str:
        return self.format

class Language(AliasableModel("Language")):
    iso_639_code = models.CharField(max_length=10, unique=True)
    english_name = models.CharField(max_length=40)
    endonym = models.CharField(max_length=40)
    child_language_of = models.ForeignKey("Language", blank=True, null=True, on_delete=models.SET_NULL, related_name="child_languages")

    def __str__(self) -> str:
        return self.iso_639_code + " - " + self.english_name + " - " + self.endonym

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

class AbstractDocument(AliasableModel("AbstractDocument")):
    """Represents an abstract document. For example, 'the first Harry Potter book', regardless of language, edition, print, etc.
    """
    original_publication_date = models.DateField(blank=True, null=True)
    authors = models.ManyToManyField(Author)
    fallback_name = models.CharField(max_length=maxFileNameLength, unique=True)

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

    existance_type = models.IntegerField(
        choices=existanceType.choices,
        default=existanceType.LOCAL,
        blank=True
    )

    #precalculated to quickly serve users and reduce load in backend
    file_url = models.CharField(max_length=maxFileNameLength, blank=True)
    last_file_update = models.DateTimeField(blank=True, default=datetime.datetime(1970, 1, 1, 1, 00))

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

class Revision(RemoteBackupModel):
    belongs_to = models.ForeignKey(Edition, on_delete=models.CASCADE, related_name="revisions")
    date = models.DateTimeField(blank=True, auto_now_add=True)
    entry_file = models.ForeignKey("File", null=True, blank=True, on_delete=models.CASCADE)

    @staticmethod
    def cleanOldRevisions():
        #TODO implement
        raise NotImplementedError()

class File(RemoteBackupModel):
    belongs_to = models.ForeignKey(Revision, on_delete=models.CASCADE, related_name="files")
    file_format = models.ForeignKey(FileFormat, on_delete=models.CASCADE)
    filename = models.CharField(max_length=maxFileNameLength)

    #TODO implement on delete clean file methodes

    @staticmethod
    def cleanOldFiles():
        raise NotImplementedError()

# Auto Generation configuration
class AutoGenerationConfig(models.Model):
    name = models.CharField(max_length=100)
    script_name = models.CharField(max_length=100)
    description = models.CharField(max_length=500, blank=True)
    automatically_regenerate = models.BooleanField(default=False)
    source_file_format = models.ForeignKey(FileFormat, on_delete=models.CASCADE, related_name='can_be_consumed_by_autogen', null=True)
    target_file_format = models.ForeignKey(FileFormat, on_delete=models.CASCADE, related_name='can_be_generated_by_autogen', null=True)
    config_json = models.CharField(max_length=500, default="{}")

# Saves all auto generated files with their configuration so they can be regenerated if needed.
class AutoGeneration(models.Model):
    config = models.ForeignKey(AutoGenerationConfig, on_delete=models.CASCADE)
    original = models.ForeignKey(Edition, related_name="generation_dependencies", on_delete=models.CASCADE)
    generated_version = models.OneToOneField(
        Edition,
        on_delete=models.CASCADE,
        primary_key=True,
    )