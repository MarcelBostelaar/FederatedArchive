from django.contrib import admin

from archive_backend.utils.small import HttpUtil
from .abstract_admin import RemoteAdminView
from archive_backend.models import *
from archive_backend.api import RemotePeerViews

class AliasAdminModel(admin.ModelAdmin):
    readonly_fields = ('alias_identifier',)
    list_display = ["origin", "target", "alias_identifier"]
    
    def alias_identifier(self, obj):
        return obj.origin.alias_identifier

class RemotePeerAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        if not change:
            url = RemotePeerViews.get_list_url(obj.site_adress, only_self=True)
            data = HttpUtil().get_json_from_remote(url)[0]
            obj.site_name = data["site_name"]
            obj.id = data["id"]
        super().save_model(request, obj, form, change)

admin.site.register(RemotePeer, RemotePeerAdmin)

remotes = [
    AuthorDescriptionTranslation,
    AbstractDocumentDescriptionTranslation,
    Edition, Revision, ArchiveFile 
           ]

remotesAliasable = [
    FileFormat, Language, Author, AbstractDocument
]

for i in remotes:
    admin.site.register(i, RemoteAdminView)

for i in remotesAliasable:
    admin.site.register(i, RemoteAdminView)
    admin.site.register(archiveAppConfig.get_model(i.__name__ + "AliasThrough"))
    

admin.site.register(GenerationConfig)