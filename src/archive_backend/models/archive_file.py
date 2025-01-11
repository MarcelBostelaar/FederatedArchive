from pathlib import Path
from typing import List
import uuid
from django.db import IntegrityError, models
from archive_backend.constants import *
from archive_backend.models.revision import Revision, RevisionStatus
from archive_backend.utils.custom_storage_class import OverwriteStorage
from .file_format import FileFormat
from .util_abstract_models import RemoteModel
from django.core.files import File
from django.core.files.move import file_move_safe
from django.utils.text import get_valid_filename
from django.conf import settings
from django.utils.module_loading import import_string

class PersistentFileID(models.Model):
    """An id that links all variations and revisions of a file together, accross revisions and editions, merges or splits."""
    ## Developer justification
    # This is currently implemented as a seperate model, with a m2m relation between this and the archive file.
    # Accessing a persistent id thus always incurrs the cost of an unneccecary join (as this file does 
    # not contain any additional info that needs to be loaded in the db). However, manually implementing 
    # it as a table that contians a persistent id and a FK as a unique pair required an additional pk 
    # in the django table because django does not support composite primary keys. 
    # Additionally, it would pull this logic out of django idiomacy and make it impossible to use 
    # it in advanced (chained/nested) queries (or even just going from one file to all variants of it), 
    # even if an additional dummy object was created to handle accessing alternative file versions.
    # For this reason, for idiomacy, usage of existing django tooling, and lower mental and maintanance load, 
    # this solution was chosen despite a performance cost. 
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, blank=True)


#Archive file logic

def default_file_path_generator(instance):
    return 'archive_files/' + get_valid_filename(f"{str(instance.id)} {instance.file_name}.{instance.file_format.format}")

fpg_callsign = getattr(settings, 'FILEPATH_GENERATOR', None)
if fpg_callsign is None:
    file_path_generator = default_file_path_generator
else:
    file_path_generator = import_string(fpg_callsign)

def wrapped_file_path(instance, filename):
    return file_path_generator(instance)


class ArchiveFile(RemoteModel):
    belongs_to = models.ForeignKey(Revision, on_delete=models.CASCADE, related_name="files")
    file_format = models.ForeignKey(FileFormat, on_delete=models.PROTECT)
    file = models.FileField(upload_to=wrapped_file_path, storage=OverwriteStorage())
    file_name = models.CharField(max_length=255)
    
    persistent_file_ids = models.ManyToManyField(PersistentFileID, related_name="files")
    """A list of ids which indicate that this file is, or is a variation on.
    Intended to be used to provide permanent links to files which may be revised 
     (and thus have a new file id)/change format, 
     additionally to find alternative editions of a file for large documents.

    IE a md and html version of the same file both have the same id in here, 
     and different revisions of the same file do too.

    A pdf generated from several md files would have all the PFIDs in its list,
     while md files transcribed from an original single pdf could all link the PFID of the pdf.
    
    Can be utilized to find alternative formats of any arbitrary file when linked to,
     or the most recent version of a file by filtering results on extention and date.
    """

    class Meta:
        #What file is saved as depends on filename and format, and thus should be unique to the revision
        unique_together = ["file_name", "file_format", "belongs_to"]

    def saveFile(self, file : File):
        self.file.save("unneccecary", file) #filename is set directly by the archive_file_path but the library demands we give it something
        return self

    def save(self, *args, **kwargs):
        if not ArchiveFile.objects.filter(id = self.id).exists():
            #New item
            if self.belongs_to.status == RevisionStatus.ONDISKPUBLISHED:
                raise IntegrityError("Cannot create a file for a published revision")

        if self.from_remote != self.belongs_to.from_remote:
            raise IntegrityError("Cannot create a file with a different origin: ", self.from_remote, self.belongs_to.from_remote)

        super().save(*args, **kwargs)
    
    def fix_file(self):
        """Fixed issues with the Archive File.
        Copies the on disk file to the correct location and name if needed.
        Adds a Persistent File ID if the file has none yet and the file is published."""
        self._resave_ondisk_file()
        self._create_PFID_if_needed()
        self.save()

    def _create_PFID_if_needed(self):
        if self.belongs_to.status == RevisionStatus.ONDISKPUBLISHED:
            if self.persistent_file_ids.count() == 0:
                pfid = PersistentFileID.objects.create()
                self.persistent_file_ids.add(pfid)

    def _resave_ondisk_file(self):
        old_file_uri = self.file.name
        new_file_uri = file_path_generator(self)
        if old_file_uri == new_file_uri:
            return
        Path(new_file_uri).parents[0].mkdir(parents=True, exist_ok=True)
        file_move_safe(old_file_uri, new_file_uri, allow_overwrite=True)
        self.file.name = new_file_uri


    def __str__(self):
        return self.file_name + " - " + str(self.belongs_to)
    

