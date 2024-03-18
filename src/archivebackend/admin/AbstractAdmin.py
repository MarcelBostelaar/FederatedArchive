from django.contrib import admin
from archivebackend.models import RemotePeer


class RemoteAdminView(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super(RemoteAdminView, self).get_form(request, obj, **kwargs)
        form.base_fields['from_remote'].initial = RemotePeer.objects.get(is_this_site = True)
        form.base_fields['from_remote'].disabled = True
        return form
    
    def has_change_permission(self, request, obj=None):
        if obj is None:
            return True
        if obj.from_remote is None:
            return True
        return obj.from_remote.is_this_site
        
    def has_delete_permission(self, request, obj=None):
        return self.has_change_permission(request, obj)
    
    def has_add_permission(self, request, obj=None):
        return self.has_change_permission(request, obj)
    
def make_aliases(modeladmin, request, queryset):
    if queryset.count() < 2:
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