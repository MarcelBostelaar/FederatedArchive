from django.db import IntegrityError, models
from archive_backend.constants import *
from archive_backend.models.revision_file_models import Revision
from .file_format import FileFormat
from .util_abstract_models import RemoteModel
from django.core.files import File

def archive_file_path(instance, filename):
    return 'archive_files/' + str(instance.belongs_to.pk) + '/' + instance.file_name + "." + instance.file_format.format

class ArchiveFile(RemoteModel):
    belongs_to = models.ForeignKey(Revision, on_delete=models.CASCADE, related_name="files")
    file_format = models.ForeignKey(FileFormat, on_delete=models.PROTECT)
    file = models.FileField(upload_to=archive_file_path)
    file_name = models.CharField(max_length=255)

    def saveFile(self, file : File):
        self.file.save("unneccecary", file)
        return self

    def save(self, *args, **kwargs):
        if self.from_remote != self.belongs_to.from_remote:
            raise IntegrityError("Cannot create a file with a different origin: ", self.from_remote, self.belongs_to.from_remote)

        return super().save(*args, **kwargs)
    
    def __str__(self):
        return self.file.name