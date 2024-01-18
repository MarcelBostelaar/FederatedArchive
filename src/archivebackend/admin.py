from itertools import chain
import os
from typing import Any
from django import forms
from django.contrib import admin
from ArchiveSite.settings import BASE_DIR
from archivebackend.api.uploads import uploadSeveralDocuments
from django.utils.html import mark_safe

from archivebackend.models import *

class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', 'birthday')
    search_fields = ['name', 'birthday']

class AuthorDescriptionTranslationAdmin(admin.ModelAdmin):
    list_display = ('describes', 'language_iso_639_format', 'name_translation', 'description')
    search_fields = ['describes' 'name_translation']
    list_filter = ["language_iso_639_format"]

class AbstractDocumentAdmin(admin.ModelAdmin):
    list_display = ('human_readable_id', 'original_publication_date', 'all_authors')
    search_fields = ['human_readable_id', 'original_publication_date', 'all_authors']

    def all_authors(self, obj):
        return ", ".join([p.name for p in obj.authors.all()])

class AbstractDocumentDescriptionTranslationAdmin(admin.ModelAdmin):
    list_display = ('describes', 'language_iso_639_format', 'title_translation', 'description')
    search_fields = ['describes', 'title_translation']
    list_filter = ["language_iso_639_format"]

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class EditionForm(forms.ModelForm):
    new_files = MultipleFileField(required=False)
    delete_old_files = forms.BooleanField(required=False)

    class Meta:
        model = Edition
        fields = '__all__'

class EditionAdmin(admin.ModelAdmin):
    list_display = ('edition_of', 'publication_date', 'language_iso_639_format', 'file_format', 'open_file', 'title', 'all_authors', 'description')
    search_fields = ['edition_of', 'publication_date', 'title', 'all_authors']
    list_filter = ["language_iso_639_format", 'file_format']

    form = EditionForm

    fieldsets = (
        (None, {
            'fields': ('edition_of', 'publication_date', 'language_iso_639_format', 'file_format', 'new_files', 'delete_old_files', 'title',  'description'),
        }),
    )

    def all_authors(self, obj):
        originalAuthors = obj.edition_of.authors.all()
        additionalAuthors = obj.additional_authors.all()
        return ", ".join([p.name for p in chain(originalAuthors, additionalAuthors)])

    def open_file(self, obj):
        return mark_safe("<a href='%s'>open</a>" % ("/uploads/editions/" + str(obj.pk) + "/" + obj.file_url))
    
    def save_model(self, request: Any, obj: Any, form: Any, change: Any) -> None:
        returnValue = super().save_model(request, obj, form, change)
        new_files = form.cleaned_data.get('new_files', None)
        delete_old = form.cleaned_data.get('delete_old_files', None)
        obj.file_url = uploadSeveralDocuments(os.path.join(BASE_DIR, "uploads", "editions", str(obj.pk)), delete_old, *new_files)
        obj.save()
        return returnValue
    

admin.site.register(Author, AuthorAdmin)
admin.site.register(AuthorDescriptionTranslation, AuthorDescriptionTranslationAdmin)
admin.site.register(AbstractDocument, AbstractDocumentAdmin)
admin.site.register(AbstractDocumentDescriptionTranslation, AbstractDocumentDescriptionTranslationAdmin)
admin.site.register(Edition, EditionAdmin)