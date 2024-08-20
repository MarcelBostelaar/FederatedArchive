from collections.abc import Callable, Sequence
from typing import Any
from django.contrib import admin
from django.http import HttpRequest
from archivebackend.models import RemotePeer, existanceType


class RemoteAdminView(admin.ModelAdmin):
    # def get_fields(self, request: HttpRequest, obj):
    #     return (super().fields or []) + ["from_remote"]

    def get_readonly_fields(self, request, obj=None):
        if obj is not None:
            if obj.from_remote != RemotePeer.objects.get(is_this_site = True): # Make all fields readonly if the edition is not local
                return self.fields or []
            
        return super().get_readonly_fields(request, obj) + ("from_remote",) #from remote is always readonly

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