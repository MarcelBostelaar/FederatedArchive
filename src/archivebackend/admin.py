import datetime
from itertools import chain
import os
from typing import Any
from django import forms
from django.contrib import admin
from django.contrib.admin.options import InlineModelAdmin
from django.http import HttpRequest
from ArchiveSite.settings import BASE_DIR, EDITIONS_URL
from archivebackend.api.uploads import uploadSeveralDocuments
from django.utils.html import mark_safe

from archivebackend.models import *

class RemoteAdminView(admin.ModelAdmin):
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
    if queryset.count() < 2:# TODO FIX
        return
    first = queryset[0]
    for i in queryset:
        first.addAlias(i)
    first.fixAllAliases()

class AliasableRemoteAdminView(RemoteAdminView):

    def get_exclude(self, request, obj=None):
        fromSuper = super().get_exclude(request, obj)
        return ([] if fromSuper is None else list(fromSuper)) + ["alias_identifier"]
    
    inlines = [] #TODO add in selection menu
    actions = [make_aliases]

class RemotePeerView(RemoteAdminView):
    exclude = ["is_this_site"]
    readonly_fields = ('last_checkin',)
    list_display = ('site_name', 'site_adress', 'mirror_files', 'peers_of_peer', 'is_this_site', 'from_remote')
    list_filter = ('mirror_files', 'peers_of_peer', 'from_remote', 'is_this_site')

admin.site.register(RemotePeer, RemotePeerView)

class DescriptionTranslationInline(admin.TabularInline):
    verbose_name = "Local name"
    exclude = ('from_remote',)
    def get_queryset(self, request):
        return self.model.objects.all()#.filter(from_remote__is_this_site = True)

class DescriptionTranslationRemoteInline(admin.TabularInline):
    verbose_name = "Names from remote"
    readonly_fields = ['from_remote','language','translation','description']
    def has_delete_permission(self, request, obj=None):
        return False
    def has_add_permission(self, request, obj=None):
        return False
    def has_change_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        return super().get_queryset(request).filter(from_remote__is_this_site = False)

class AuthorTranslationInline(DescriptionTranslationInline):
    model = AuthorDescriptionTranslation
class AuthorTranslationRemoteInline(DescriptionTranslationRemoteInline):
    model = AuthorDescriptionTranslation
class DocumentTranslationInline(DescriptionTranslationInline):
    model = AbstractDocumentDescriptionTranslation
class DocumentTranslationRemoteInline(DescriptionTranslationRemoteInline):
    model = AbstractDocumentDescriptionTranslation

class AuthorAdmin(AliasableRemoteAdminView):
    def get_inlines(self, request, obj=None):
        fromSuper = super().get_inlines(request, obj)
        return ([] if fromSuper is None else list(fromSuper)) + [AuthorTranslationInline, AuthorTranslationRemoteInline]

    list_display = ["fallback_name", "alias_identifier"]
    search_fields = ["fallback_name", "alias_origin_end__target__descriptions__translation"]

    def name_translations():
        return ["marcel", "bostelaar"]

    def get_queryset(self, request):
        return super().get_queryset(request).order_by("alias_identifier", "fallback_name")
    
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

class DocumentAdmin(AliasableRemoteAdminView):
    def get_inlines(self, request, obj=None):
        fromSuper = super().get_inlines(request, obj)
        return ([] if fromSuper is None else list(fromSuper)) + [DocumentTranslationInline, DocumentTranslationRemoteInline]

    list_display = ["fallback_name"]
    autocomplete_fields = ["authors"]

    def get_queryset(self, request):
        return super().get_queryset(request).order_by("alias_identifier", "fallback_name")
    
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

admin.site.register(FileFormat, AliasableRemoteAdminView)
admin.site.register(Language, AliasableRemoteAdminView)
admin.site.register(Author, AuthorAdmin)
admin.site.register(AuthorDescriptionTranslation, RemoteAdminView)
admin.site.register(AbstractDocument, DocumentAdmin)
admin.site.register(AbstractDocumentDescriptionTranslation, RemoteAdminView)
admin.site.register(Edition, RemoteAdminView)
admin.site.register(Revision, RemoteAdminView)
admin.site.register(File, RemoteAdminView)
admin.site.register(AutoGenerationConfig, RemoteAdminView)
admin.site.register(AutoGeneration, RemoteAdminView)

class dummy(admin.ModelAdmin):
    readonly_fields = ('alias_identifier',)
    list_display = ["origin", "target", "alias_identifier"]
    
    def alias_identifier(self, obj):
        return obj.origin.alias_identifier

admin.site.register(archiveAppConfig.get_model("AuthorAliasThrough"), dummy)