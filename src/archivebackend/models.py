from django.db import models

descriptionLength = 500
authorLength = 100
titleLength = 200

# Create your models here.

class Author(models.Model):
    name = models.CharField(max_length=authorLength)
    birthday = models.DateField(blank=True, null=True)

    def __str__(self) -> str:
        return self.name + " - " + str(self.birthday)

class AuthorDescriptionTranslation(models.Model):
    describes = models.ForeignKey(Author, on_delete=models.CASCADE)
    language_iso_639_format = models.CharField(max_length=2)
    name_translation = models.CharField(max_length=authorLength)
    description = models.CharField(max_length=descriptionLength, blank=True)

    def __str__(self) -> str:
        return self.name_translation + " - (" + self.language_iso_639_format + ")"

    class Meta:
        unique_together = ["describes", "language_iso_639_format"]


class AbstractDocument(models.Model):
    """Represents an abstract document. For example, 'the first Harry Potter book', regardless of language, edition, print, etc.
    A workable id system must be established on a per-project basis. 
    A possibility is <the author + year + original book title in the original language, in common latin transliteration>
    """
    human_readable_id = models.CharField(max_length=200, unique=True)
    original_publication_date = models.DateField(blank=True, null=True)
    authors = models.ManyToManyField(Author)

    def __str__(self) -> str:
        return self.human_readable_id

class AbstractDocumentDescriptionTranslation(models.Model):
    """Provides functionality for adding titles and descriptions of abstract documents in multiple languages"""
    describes = models.ForeignKey(AbstractDocument, on_delete=models.CASCADE)
    language_iso_639_format = models.CharField(max_length=2)
    title_translation = models.CharField(max_length=titleLength)
    description = models.CharField(max_length=descriptionLength, blank=True)

    def __str__(self) -> str:
        return self.title_translation + " - (" + self.language_iso_639_format + ")"

    class Meta:
        unique_together = ["describes", "language_iso_639_format"]


class Edition(models.Model):
    edition_of = models.ForeignKey(AbstractDocument, on_delete=models.CASCADE)
    publication_date = models.DateField(blank=True, null=True)
    language_iso_639_format = models.CharField(max_length=2)
    file_format = models.CharField(max_length=10)
    title = models.CharField(max_length=titleLength)
    description = models.CharField(max_length=descriptionLength)
    additional_authors = models.ManyToManyField(Author, blank=True)
    # file = models.FileField(upload_to='uploads/')

    def __str__(self) -> str:
        return self.title + " - (" + self.language_iso_639_format + ") - " + self.file_format