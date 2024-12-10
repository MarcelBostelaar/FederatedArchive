from django.db import models
from .remote_model import RemoteModel

class RemoteBackupModel(RemoteModel):
    """
    Backupable Remote models may be protected from being overridden during a sync, or being deleted when a new revision is created, by setting the is_backup flag to True.

    This will prevent propagation of malicious edits in a root archive/source server to its backups/mirrors,
    such as with a hostile takeover of the server.
    
    Alternatively, it may be used for more permantent versioning purposes.
    """
    is_backup = models.BooleanField(blank=True, default=False)

    class Meta:
        abstract = True