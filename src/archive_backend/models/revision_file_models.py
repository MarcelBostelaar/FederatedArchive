import datetime
from django import forms
from django.db import models
from archive_backend.constants import *
from .file_format import FileFormat
from .edition_models import Edition
from .util_abstract_models import RemoteBackupModel

class RevisionStatus(models.IntegerChoices):
    ONDISK = 0
    REQUESTABLE = 1
    JOBSCHEDULED = 2

class Revision(RemoteBackupModel):
    belongs_to = models.ForeignKey(Edition, on_delete=models.CASCADE, related_name="revisions")
    date = models.DateTimeField(blank=True, auto_now_add=True)
    entry_file = models.ForeignKey("File", null=True, blank=True, on_delete=models.CASCADE)
    status = models.IntegerField(choices=RevisionStatus.choices, default=RevisionStatus.ONDISK, blank=True)

class File(RemoteBackupModel):
    belongs_to = models.ForeignKey(Revision, null=True, on_delete=models.CASCADE, related_name="files")
    file_format = models.ForeignKey(FileFormat, on_delete=models.PROTECT)
    filename = models.CharField(max_length=maxFileNameLength)
