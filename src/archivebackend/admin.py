import datetime
from itertools import chain
import os
from typing import Any
from django import forms
from django.contrib import admin
from django.http import HttpRequest
from ArchiveSite.settings import BASE_DIR, EDITIONS_URL
from archivebackend.api.uploads import uploadSeveralDocuments
from django.utils.html import mark_safe

from archivebackend.models import *

# class PeerAdmin(admin.ModelAdmin):
#     list_display = ("site_name", "site_adress", "mirror_files", "last_checkin")
#     search_fields = ("site_name", "site_adress")
#     list_filter = ["mirror_files"]

# class LanguageAdmin(admin.ModelAdmin):
#     list_display = ('iso_639_code', 'english_name', "endonym", "child_language_of")
#     search_fields = ['iso_639_code', 'english_name', "endonym", "child_language_of"]
#     readonly_fields=["from_remote"]

# class AuthorAdmin(admin.ModelAdmin):
#     list_display = ('name', 'birthday')
#     search_fields = ['name', 'birthday']
#     readonly_fields=["from_remote"]

# class AuthorDescriptionTranslationAdmin(admin.ModelAdmin):
#     list_display = ('describes', 'language', 'name_translation', 'description')
#     search_fields = ['describes' 'name_translation']
#     list_filter = ["language"]
#     readonly_fields=["from_remote"]

# class AbstractDocumentAdmin(admin.ModelAdmin):
#     list_display = ('human_readable_id', 'original_publication_date', 'all_authors')
#     search_fields = ['human_readable_id', 'original_publication_date', 'all_authors']
#     readonly_fields=["from_remote"]

#     def all_authors(self, obj):
#         return ", ".join([p.name for p in obj.authors.all()])

# class AbstractDocumentDescriptionTranslationAdmin(admin.ModelAdmin):
#     list_display = ('describes', 'language', 'title_translation', 'description')
#     search_fields = ['describes', 'title_translation']
#     list_filter = ["language"]
#     readonly_fields=["from_remote"]

# class MultipleFileInput(forms.ClearableFileInput):
#     allow_multiple_selected = True


# class MultipleFileField(forms.FileField):
#     def __init__(self, *args, **kwargs):
#         kwargs.setdefault("widget", MultipleFileInput())
#         super().__init__(*args, **kwargs)

#     def clean(self, data, initial=None):
#         single_file_clean = super().clean
#         if isinstance(data, (list, tuple)):
#             result = [single_file_clean(d, initial) for d in data]
#         else:
#             result = single_file_clean(data, initial)
#         return result

# class LocalEdition(Edition):
#     class Meta:
#         proxy = True

# # class GeneratedEdition(Edition):
# #     class Meta:
# #         proxy = True

# # class RemoteEdition(Edition):
# #     class Meta:
# #         proxy = True

# class LocalEditionForm(forms.ModelForm):
#     new_files = MultipleFileField(required=False)
#     delete_old_files = forms.BooleanField(required=False)

#     class Meta:
#         model = LocalEdition
#         fields = '__all__'

# class LocalEditionAdmin(admin.ModelAdmin):
#     list_display = ('edition_of', 'publication_date', 'language', 'file_format', 'open_file', 'title', 'all_authors', 'description', "is_fork")
#     search_fields = ['edition_of', 'publication_date', 'title', 'all_authors']
#     list_filter = ["language", 'file_format']
#     readonly_fields=["from_remote"]

#     form = LocalEditionForm

#     fieldsets = (
#         (None, {
#             'fields': ('edition_of', 'publication_date', 'language', 'file_format', 'new_files', 'delete_old_files', 'title',  'description'),
#         }),
#     )

#     def all_authors(self, obj):
#         originalAuthors = obj.edition_of.authors.all()
#         additionalAuthors = obj.additional_authors.all()
#         return ", ".join([p.name for p in chain(originalAuthors, additionalAuthors)])

#     def open_file(self, obj):
#         return mark_safe("<a href='%s'>open</a>" % ("/uploads/editions/" + str(obj.pk) + "/" + obj.file_url))
    
#     def save_model(self, request: Any, obj: Any, form: Any, change: Any) -> None:
#         returnValue = super().save_model(request, obj, form, change)
#         new_files = form.cleaned_data.get('new_files', None)
#         delete_old = form.cleaned_data.get('delete_old_files', None)
#         if(len(new_files) > 0 or delete_old):
#             obj.file_url = uploadSeveralDocuments(os.path.join(EDITIONS_URL, str(obj.pk)), delete_old, *new_files)
#             obj.last_file_update = datetime.now()
#             obj.save()
#         return returnValue
    
#     def is_fork(self, obj):
#         return obj.existance_type == existanceType.LOCALFORK
    
#     def get_queryset(self, request):
#         """
#         Filter the objects displayed in the change_list to only
#         display those for the currently signed in user.
#         """
#         qs = super(LocalEditionAdmin, self).get_queryset(request)
#         return qs.filter(existance_type__in=[existanceType.LOCAL, existanceType.LOCALFORK])
    

# admin.site.register(RemotePeer, PeerAdmin)
# admin.site.register(Language, LanguageAdmin)
# admin.site.register(Author, AuthorAdmin)
# admin.site.register(AuthorDescriptionTranslation, AuthorDescriptionTranslationAdmin)
# admin.site.register(AbstractDocument, AbstractDocumentAdmin)
# admin.site.register(AbstractDocumentDescriptionTranslation, AbstractDocumentDescriptionTranslationAdmin)
# admin.site.register(LocalEdition, LocalEditionAdmin)


class RemoteAdminView(admin.ModelAdmin):
    # readonly_fields = ["from_remote"]
    def get_form(self, request, obj=None, **kwargs):
        form = super(RemoteAdminView, self).get_form(request, obj, **kwargs)
        form.base_fields['from_remote'].initial = RemotePeer.objects.get(is_this_site = True)
        form.base_fields['from_remote'].disabled = True
        return form
    
    def has_change_permission(self, request: HttpRequest, obj=None):
        if obj is None:
            return True
        if obj.from_remote is None:
            return True
        return obj.from_remote.is_this_site
        
    def has_delete_permission(self, request: HttpRequest, obj=None):
        return self.has_change_permission(request, obj)
    
    def has_add_permission(self, request: HttpRequest, obj=None):
        return self.has_change_permission(request, obj)
    
def make_aliases(modeladmin, request, queryset):
    if queryset.count == 0:
        return
    first = queryset[0]
    for i in queryset:
        first.addAlias(i)

class AliasableRemoteAdminView(RemoteAdminView):
    actions = [make_aliases]

    # def get_queryset(self):
        # return self.queryset.order_by(/*sort by alias group then by name*/)



class RemotePeerView(RemoteAdminView):
    exclude = ["is_this_site"]
    readonly_fields = ('last_checkin',)
    list_display = ('site_name', 'site_adress', 'mirror_files', 'peers_of_peer', 'is_this_site', 'from_remote')
    list_filter = ('mirror_files', 'peers_of_peer', 'from_remote', 'is_this_site')

admin.site.register(RemotePeer, RemotePeerView)


class AuthorDescriptionTranslationInline(admin.TabularInline):
    verbose_name = "Local names"
    exclude = ('from_remote',)
    model = AuthorDescriptionTranslation
    def get_queryset(self, request):
        return super().get_queryset(request).filter(from_remote = RemotePeer.objects.get(is_this_site = True))
class AuthorDescriptionTranslationRemoteInline(admin.TabularInline):
    verbose_name = "Names from remote"
    readonly_fields = ['from_remote','language','name_translation','description']
    model = AuthorDescriptionTranslation
    def has_delete_permission(self, request, obj=None):
        return False
    def has_add_permission(self, request, obj=None):
        return False
    def has_change_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        return super().get_queryset(request).filter(from_remote = RemotePeer.objects.get(is_this_site = False))

class AuthorAdmin(AliasableRemoteAdminView):
    inlines = [AuthorDescriptionTranslationInline, AuthorDescriptionTranslationRemoteInline]

    def save_related(self, request, form, formsets, change):
        """
        Override the save_related method to intercept the saving of the inline formset.
        """
        for formset in formsets:
            if formset.prefix == 'descriptions':
                for instance in formset.save(commit=False):
                    if instance.from_remote_id is None:
                        instance.from_remote_id = RemotePeer.objects.get(is_this_site = True).id
        super().save_related(request, form, formsets, change)

admin.site.register(FileFormat, RemoteAdminView)
admin.site.register(Language, RemoteAdminView)
admin.site.register(Author, AuthorAdmin)
admin.site.register(AuthorDescriptionTranslation, RemoteAdminView)
admin.site.register(AbstractDocument, RemoteAdminView)
admin.site.register(AbstractDocumentDescriptionTranslation, RemoteAdminView)
admin.site.register(Edition, RemoteAdminView)
admin.site.register(Revision, RemoteAdminView)
admin.site.register(File, RemoteAdminView)
admin.site.register(AutoGenerationConfig, RemoteAdminView)
admin.site.register(AutoGeneration, RemoteAdminView)

class dummy(admin.ModelAdmin):
    list_display = ["origin", "target", "alias_identifier"]

admin.site.register(archiveAppConfig.get_model("AuthorAliasThrough"), dummy)