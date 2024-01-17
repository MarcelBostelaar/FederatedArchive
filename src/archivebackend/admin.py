from itertools import chain
from django.contrib import admin

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

class EditionAdmin(admin.ModelAdmin):
    list_display = ('edition_of', 'publication_date', 'language_iso_639_format', 'file_format', 'file', 'title', 'all_authors', 'description')
    search_fields = ['edition_of', 'publication_date', 'title', 'all_authors']
    list_filter = ["language_iso_639_format", 'file_format']

    def all_authors(self, obj):
        originalAuthors = obj.edition_of.authors.all()
        additionalAuthors = obj.additional_authors.all()
        return ", ".join([p.name for p in chain(originalAuthors, additionalAuthors)])
    
    # def file(self, obj):
    #     return "placeholder"
    
    # def save(self, commit=True):
    #     extra_field = self.cleaned_data.get('extra_field', None)
    #     # ...do something with extra_field here...
    #     return super(EditionAdmin, self).save(commit=commit)

    # class Meta:
    #     model = Edition

admin.site.register(Author, AuthorAdmin)
admin.site.register(AuthorDescriptionTranslation, AuthorDescriptionTranslationAdmin)
admin.site.register(AbstractDocument, AbstractDocumentAdmin)
admin.site.register(AbstractDocumentDescriptionTranslation, AbstractDocumentDescriptionTranslationAdmin)
admin.site.register(Edition, EditionAdmin)