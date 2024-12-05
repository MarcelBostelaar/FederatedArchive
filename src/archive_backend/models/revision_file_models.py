import datetime
from django import forms
from django.db import models
from archive_backend.constants import *
from .file_format import FileFormat
from .edition_models import Edition, existanceType
from .util_abstract_models import RemoteBackupModel

class RevisionStatus(models.IntegerChoices):
    ONDISKPUBLISHED = 0
    REQUESTABLE = 1
    JOBSCHEDULED = 2
    UNFINISHED = 4

class Revision(RemoteBackupModel):
    belongs_to = models.ForeignKey(Edition, on_delete=models.CASCADE, related_name="revisions")
    date = models.DateTimeField(blank=True, auto_now_add=True)
    entry_file = models.ForeignKey("File", null=True, blank=True, on_delete=models.CASCADE)
    _status = models.IntegerField(choices=RevisionStatus.choices, default=RevisionStatus.UNFINISHED, blank=True)

    @property
    def status(self):
        return self._status
    
    @status.setter
    def status(self, newState):
        if self._status == newState:
            return
        if self._status == None:
            #Checks for new revision creation
            if newState == RevisionStatus.ONDISKPUBLISHED:
                if self.edition.existance_type != existanceType.LOCAL:
                    raise ValueError("""Cannot immediately create a local revision, as files do not exists, 
                                     which can make autogeneration not work. Make a UNFINISHED revision first, 
                                     then change its status to ONDISKPUBLISHED when it is done.""")
            self._status = newState
            return
        match [self._status, newState]:
            case [_, RevisionStatus.ONDISKPUBLISHED]:
                self._status = newState
                return
            case [_, RevisionStatus.UNFINISHED]:
                raise ValueError("Cannot change status to UNFINISHED, UNFINISHED can only be an initial state.")
            case [RevisionStatus.REQUESTABLE, RevisionStatus.JOBSCHEDULED]:
                self._status = newState
                return
            case _:
                raise ValueError("Cannot change status from {} to {}".format(self._status, newState))

class File(RemoteBackupModel):
    belongs_to = models.ForeignKey(Revision, null=True, on_delete=models.CASCADE, related_name="files")
    file_format = models.ForeignKey(FileFormat, on_delete=models.PROTECT)
    filename = models.CharField(max_length=maxFileNameLength)
    file = models.FileField(upload_to='archive_files/')
