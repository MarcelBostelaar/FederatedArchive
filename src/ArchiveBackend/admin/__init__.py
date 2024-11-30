from django.contrib import admin
from .AbstractAdmin import RemoteAdminView
from ArchiveBackend.models import *


class AliasAdminModel(admin.ModelAdmin):
    readonly_fields = ('alias_identifier',)
    list_display = ["origin", "target", "alias_identifier"]
    
    def alias_identifier(self, obj):
        return obj.origin.alias_identifier


remotes = [
    RemotePeer, AuthorDescriptionTranslation,
    AbstractDocumentDescriptionTranslation,
    Edition, Revision, File 
           ]

remotesAliasable = [
    FileFormat, Language, Author, AbstractDocument
]

for i in remotes:
    admin.site.register(i, RemoteAdminView)

for i in remotesAliasable:
    admin.site.register(i, RemoteAdminView)
    admin.site.register(archiveAppConfig.get_model(i.__name__ + "AliasThrough"), AliasAdminModel)
    

admin.site.register(AutoGenerationConfig)
admin.site.register(AutoGeneration)
admin.site.register(Job)