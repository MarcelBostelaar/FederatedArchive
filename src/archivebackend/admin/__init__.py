from django.contrib import admin
from archivebackend.admin.AbstractAdmin import AliasableRemoteAdminView, RemoteAdminView
from archivebackend.admin.Authors import AuthorAdmin
from archivebackend.admin.Document import DocumentAdmin
from archivebackend.admin.Edition import EditionAdmin
from archivebackend.admin.InlineTranslations import *
from archivebackend.admin.RemoteViewPeer import RemotePeerView
from archivebackend.models import *

admin.site.register(RemotePeer, RemotePeerView)
admin.site.register(FileFormat, AliasableRemoteAdminView)
admin.site.register(Language, AliasableRemoteAdminView)
admin.site.register(Author, AuthorAdmin)
admin.site.register(AuthorDescriptionTranslation, RemoteAdminView)
admin.site.register(AbstractDocument, DocumentAdmin)
admin.site.register(AbstractDocumentDescriptionTranslation, RemoteAdminView)
admin.site.register(Edition, EditionAdmin)
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