import datetime
from django import forms
from django.db import models
from archivebackend.constants import *
from .FileFormat import FileFormat
from .Edition import Edition
from .modelsAbstract import RemoteBackupModel

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