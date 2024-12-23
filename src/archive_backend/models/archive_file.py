from django.db import IntegrityError, models
from archive_backend.constants import *
from archive_backend.models.revision import Revision, RevisionStatus
from archive_backend.utils.custom_storage_class import OverwriteStorage
from .file_format import FileFormat
from .util_abstract_models import RemoteModel
from django.core.files import File
from django.core.files.storage import FileSystemStorage

def archive_file_path(instance, filename):
    return 'archive_files/' + str(instance.belongs_to.pk) + '/' + instance.file_name + "." + instance.file_format.format

class ArchiveFile(RemoteModel):
    belongs_to = models.ForeignKey(Revision, on_delete=models.CASCADE, related_name="files")
    file_format = models.ForeignKey(FileFormat, on_delete=models.PROTECT)
    file = models.FileField(upload_to=archive_file_path, storage=OverwriteStorage())
    file_name = models.CharField(max_length=255)

    class Meta:
        #What file is saved as depends on filename and format, and thus should be unique to the revision
        unique_together = ["file_name", "file_format", "belongs_to"]

    def saveFile(self, file : File):
        self.file.save("unneccecary", file) #filename is set directly by the archive_file_path but the library demands we give it something
        return self

    def save(self, *args, **kwargs):
        if self.id is None:
            #New item
            if self.belongs_to.status == RevisionStatus.ONDISKPUBLISHED:
                raise IntegrityError("Cannot create a file for a published revision")

        if self.from_remote != self.belongs_to.from_remote:
            raise IntegrityError("Cannot create a file with a different origin: ", self.from_remote, self.belongs_to.from_remote)

        return super().save(*args, **kwargs)
    
    def __str__(self):
        return self.file_name + " - " + str(self.belongs_to)