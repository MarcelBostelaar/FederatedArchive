import string
from django.db import models
from archivebackend.constants import *
from .modelsAbstract import AliasableModel


class FileFormat(AliasableModel("FileFormat")):
    format = models.CharField(max_length=10)
    
    def save(self, *args, **kwargs):
        parsedFormat = self.format.replace(" ", "").replace(".", "").lower()
        if not set(parsedFormat) <= set(string.ascii_lowercase + string.digits):
            raise Exception("File format can only contain letters and numbers")
        super(FileFormat, self).save(*args, **kwargs)
    
    def __str__(self) -> str:
        return self.format