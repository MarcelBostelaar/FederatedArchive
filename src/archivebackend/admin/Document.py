
from archivebackend.admin.AbstractAdmin import AliasableRemoteAdminView
from archivebackend.admin.InlineTranslations import DocumentTranslationInline, DocumentTranslationRemoteInline
from archivebackend.models import RemotePeer


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
