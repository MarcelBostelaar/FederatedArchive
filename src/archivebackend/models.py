import datetime
import string
from django.db import models
from archivebackend.constants import *
from archivebackend.modelsAbstract import AliasableModel, RemoteModel

class existanceType(models.IntegerChoices):
    """Describes how the edition exists on this server"""
    LOCAL = 0 # Basic local files
    UNGENERATED = 1 # It should be generated from another file.
    AUTOGENERATED = 2 # It is auto generated on our server from a different file.
    REMOTE = 3 # It exists on a remote server, but isnt mirrored. Just links to the remote file. (saves storage)
    MIRROREDREMOTE = 4 # It exists on a remote server, and is copied locally by this instance for reliability/speed/archival purposes.

#Utility models

class RemotePeer(RemoteModel):
    site_name = models.CharField(max_length=titleLength)
    site_adress = models.CharField(max_length=maxFileNameLength)
    mirror_files = models.BooleanField(blank=True, default=False)
    peers_of_peer = models.BooleanField(blank=True, default=True)
    last_checkin = models.DateTimeField()

    def __str__(self) -> str:
        return self.site_name
    
class FileFormat(models.Model):
    format = models.CharField(max_length=10, unique=True)
    
    def save(self, *args, **kwargs):
        parsedFormat = self.format.replace(" ", "").replace(".", "").lower()
        if not set(parsedFormat) <= set(string.ascii_lowercase + string.digits):
            raise Exception("File format can only contain letters and numbers")
        super(FileFormat, self).save(*args, **kwargs)
    
    def __str__(self) -> str:
        return self.format

class Language(RemoteModel): #Should this even be remoteable? Should it be aliasable?
    iso_639_code = models.CharField(max_length=10, unique=True)
    english_name = models.CharField(max_length=40)
    endonym = models.CharField(max_length=40)
    child_language_of = models.ForeignKey("Language", blank=True, null=True, on_delete=models.SET_NULL, related_name="child_languages")

    def __str__(self) -> str:
        return self.iso_639_code + " - " + self.english_name


#Core models

class Author(RemoteModel, AliasableModel("Author")):
    name = models.CharField(max_length=authorLength)
    birthday = models.DateField(blank=True, null=True)

    def __str__(self) -> str:
        return self.name + " - " + str(self.birthday)

class AuthorDescriptionTranslation(RemoteModel):
    describes = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="descriptions")
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    name_translation = models.CharField(max_length=authorLength)
    description = models.CharField(max_length=descriptionLength, blank=True)

    def __str__(self) -> str:
        return self.name_translation + " - (" + self.language.iso_639_code + ")"

    class Meta:
        unique_together = ["describes", "language"]


class AbstractDocument(RemoteModel, AliasableModel("AbstractDocument")):
    """Represents an abstract document. For example, 'the first Harry Potter book', regardless of language, edition, print, etc.
    A workable id system must be established on a per-project basis. 
    A possibility is <the author + year + original book title in the original language, in common latin transliteration>
    """
    human_readable_id = models.CharField(max_length=200, unique=True)
    original_publication_date = models.DateField(blank=True, null=True)
    authors = models.ManyToManyField(Author)

    def __str__(self) -> str:
        return self.human_readable_id

class AbstractDocumentDescriptionTranslation(RemoteModel):
    """Provides functionality for adding titles and descriptions of abstract documents in multiple languages"""
    describes = models.ForeignKey(AbstractDocument, on_delete=models.CASCADE, related_name="descriptions")
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    title_translation = models.CharField(max_length=titleLength)
    description = models.CharField(max_length=descriptionLength, blank=True)

    def __str__(self) -> str:
        return self.title_translation + " - (" + self.language.iso_639_code + ")"

    class Meta:
        unique_together = ["describes", "language"]


class Edition(RemoteModel):
    """An edition is a concrete form of an abstract document. A specific printing, a specific digital form, a specific file format, with a specific language
    It can have additional authors (such as translators, preface writers, etc). It represents the whole history of this document, 
    so any textual corrections in the transcription, for example, are not grounds for a new "edition",
    unless explicit differentiation is desired such as archiving several historic prints of the same general book."""
    edition_of = models.ForeignKey(AbstractDocument, on_delete=models.CASCADE, related_name="editions")
    publication_date = models.DateField(blank=True, null=True)
    language = models.ManyToManyField(Language, on_delete=models.CASCADE)
    additional_authors = models.ManyToManyField(Author, blank=True)
    
    title = models.CharField(max_length=titleLength)
    description = models.CharField(max_length=descriptionLength)

    generated_from = models.ForeignKey("Edition", on_delete=models.SET_NULL, blank=True, null=True, related_name="generation_dependencies")
    existance_type = models.IntegerField(
        choices=existanceType.choices,
        default=existanceType.LOCAL,
        blank=True
    )

    #precalculated to quickly serve users and reduce load in backend
    file_url = models.CharField(max_length=maxFileNameLength, blank=True)
    last_file_update = models.DateTimeField(blank=True, default=datetime.datetime(1970, 1, 1, 1, 00))
    
    def save(self, *args, **kwargs):
        #TODO disallow making existance type go from anything else to Local, local forks must be explicitly made as new instances.
        super(Edition, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return self.title + " - (" + self.language.iso_639_code + ") - " + self.file_format


class Revision(RemoteModel):
    belongs_to = models.ForeignKey(Edition, on_delete=models.CASCADE, related_name="revisions")
    #Backup revisions are saved even if a newer revision exists 
    # to prevent propagation of malicious edits in a root archive to its backups, 
    # such as with a hostile takeover of the server
    is_backup_revision = models.BooleanField(blank=True, default=False)
    date = models.DateTimeField(blank=True, auto_now_add=True)
    entry_file = models.ForeignKey("File", null=True, blank=True, on_delete=models.CASCADE)

    @staticmethod
    def cleanOldRevisions():
        raise NotImplementedError()


class File(RemoteModel):
    belongs_to = models.ForeignKey(Revision, on_delete=models.CASCADE, related_name="files")
    file_format = models.ForeignKey(FileFormat, on_delete=models.CASCADE)