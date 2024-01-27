import datetime
import string
from typing import Generic, Type
import uuid
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import pre_save
from archivebackend.constants import *

#Abstract class
class RemoteModel(models.Model):
    """Contains fields and functionality to turn a model remote mirrorable"""
    from_remote = models.ForeignKey("RemotePeer", blank=True, null=True, on_delete=models.CASCADE)
    # Using UUIDs as primary keys to allows the direct merging of databases without pk and fk conflicts (unless you're astronimically unlucky).
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    class Meta:
        abstract = True

#Abstract class
def AliasableModel(nameOfOwnClass: string):
    """Contains fields and functionality to allow an entry to be an alias of another entry of the same type"""
    class AliasableModel_(RemoteModel):
        alias = models.ManyToManyField(nameOfOwnClass)

        # @classmethod
        # def fix_aliases(cls):
        #     cls.objects.
        
        #TODO
        #Dynamically create a through class and add it as a through class
        #Add that class to the globals through globals()
        #Implement specific rectification operations in this through class
        #Add utility functions on aliasable model to operate the alias functionality for user friendlyness
        #This way each Aliasable model has its own through table with automatic rectifications
        #do add an identity alias for each entry to make querying the set of all valid choices easy

        class Meta:
            abstract = True
    return AliasableModel_

class RemotePeer(RemoteModel):
    site_name = models.CharField(max_length=titleLength)
    site_adress = models.CharField(max_length=maxFileNameLength)
    mirror_files = models.BooleanField(blank=True, default=False)
    peers_of_peer = models.BooleanField(blank=True, default=True)
    last_checkin = models.DateTimeField()

    def __str__(self) -> str:
        return self.site_name

class Language(RemoteModel):
    iso_639_code = models.CharField(max_length=10, unique=True)
    english_name = models.CharField(max_length=40)
    endonym = models.CharField(max_length=40)
    child_language_of = models.ForeignKey("Language", blank=True, null=True, on_delete=models.SET_NULL, related_name="child_languages")

    def __str__(self) -> str:
        return self.iso_639_code + " - " + self.english_name

class Author(AliasableModel("Author")):
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


class AbstractDocument(AliasableModel("AbstractDocument")):
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
    edition_of = models.ForeignKey(AbstractDocument, on_delete=models.CASCADE, related_name="editions")
    publication_date = models.DateField(blank=True, null=True)
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    generated_from = models.ForeignKey("Edition", on_delete=models.SET_NULL, blank=True, null=True, related_name="generation_dependencies")
    title = models.CharField(max_length=titleLength)
    description = models.CharField(max_length=descriptionLength)
    additional_authors = models.ManyToManyField(Author, blank=True)
    #precalculated hyperlink value to quickly serve users
    file_url = models.CharField(max_length=maxFileNameLength, blank=True)
    #how is the document saved, fully local settings.
    last_file_update = models.DateTimeField(blank=True, default=datetime.datetime(1970, 1, 1, 1, 00))
    

    def __str__(self) -> str:
        return self.title + " - (" + self.language.iso_639_code + ") - " + self.file_format


class existanceType(models.IntegerChoices):
    """Describes how the edition exists on this server"""
    LOCAL = 0 # Basic local files
    UNGENERATED = 1 # It should be generated from another file.
    AUTOGENERATED = 2 # It is auto generated on our server from a different file.
    REMOTE = 3 # It exists on a remote server, but isnt mirrored. Just links to the remote file. (saves storage)
    MIRROREDREMOTE = 4 # It exists on a remote server, and is copied locally by this instance for reliability/speed/archival purposes.

class Revision(RemoteModel):
    belongs_to = models.ForeignKey(Edition, on_delete=models.CASCADE, related_name="revisions")
    #Backup revisions are saved even if a newer revision exists to prevent
    #propagation of malicious edits in a root archive to its backups
    is_backup_revision = models.BooleanField(blank=True, default=False)
    date = models.DateTimeField(blank=True, auto_now_add=True)
    entry_file = models.ForeignKey("File", null=True, blank=True, on_delete=models.CASCADE)
    existance_type = models.IntegerField(
        choices=existanceType.choices,
        default=existanceType.LOCAL,
    )

    @staticmethod
    def cleanOldRevisions():
        raise NotImplementedError()

class FileFormat(models.Model):
    format = models.CharField(max_length=10, unique=True)
    
    def save(self, *args, **kwargs):
        parsedFormat = self.format.replace(" ", "").replace(".", "").lower()
        if not set(parsedFormat) <= set(string.ascii_lowercase + string.digits):
            raise Exception("File format can only contain letters and numbers")
        super(FileFormat, self).save(*args, **kwargs)
    
    def __str__(self) -> str:
        return self.format


class File(RemoteModel):
    belongs_to = models.ForeignKey(Revision, on_delete=models.CASCADE, related_name="files")
    file_format = models.ForeignKey(FileFormat, on_delete=models.CASCADE)