from django.db import models
from archive_backend.constants import *
from .modelsAbstract import AliasableModel



class Language(AliasableModel("Language")):
    iso_639_code = models.CharField(max_length=10)
    english_name = models.CharField(max_length=40)
    endonym = models.CharField(max_length=40)
    child_language_of = models.ForeignKey("Language", blank=True, null=True, on_delete=models.SET_NULL, related_name="child_languages")

    def __str__(self) -> str:
        return self.iso_639_code + " - " + self.english_name + " - " + self.endonym
