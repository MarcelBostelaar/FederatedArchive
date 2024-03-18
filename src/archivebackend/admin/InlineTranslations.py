from archivebackend.models import AbstractDocumentDescriptionTranslation, AuthorDescriptionTranslation
from django.contrib import admin


class DescriptionTranslationInline(admin.TabularInline):
    verbose_name = "Local name"
    exclude = ('from_remote',)
    def get_queryset(self, request):
        return self.model.objects.all().filter(from_remote__is_this_site = True)

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
