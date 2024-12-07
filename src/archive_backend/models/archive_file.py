from django.db import IntegrityError, models
from archive_backend.constants import *
from archive_backend.models.revision_file_models import Revision
from .file_format import FileFormat
from .util_abstract_models import RemoteModel

class ArchiveFile(RemoteModel):
    belongs_to = models.ForeignKey(Revision, on_delete=models.CASCADE, related_name="files")
    file_format = models.ForeignKey(FileFormat, on_delete=models.PROTECT)
    file = models.FileField(upload_to=lambda instance, filename: 'archive_files/' + str(instance.belongs_to.pk) + '/' + filename)

    def save(self, *args, **kwargs):
        if self.from_remote != self.belongs_to.from_remote:
            raise IntegrityError("Cannot create a file with a different origin: ", self.from_remote, self.belongs_to.from_remote)

        return super().save(*args, **kwargs)
    
    def __str__(self):
        return self.file.name