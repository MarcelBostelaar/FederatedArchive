from django.contrib import admin
from django.db.models import Count

from .models import *

# Register your models here.

def execute_suggestion(modeladmin, request, queryset):
    for suggestion in queryset:
        suggestion.execute_suggestion()

def clean_invalid_alias_suggestions(modeladmin, request, queryset):
    items = (queryset
    .annotate(unprocessed_count=Count('unprocessed'))
    .annotate(rejected_count=Count('rejected'))
    .annotate(accepted_count=Count('accepted'))
    .filter(unprocessed_count__lte = 1)
    .filter(rejected_count__lte = 1)
    .filter(accepted_count__lte = 1)
    )
    for i in items:
        i.delete()


class SuggestionAdmin(admin.ModelAdmin):
    actions = [execute_suggestion, clean_invalid_alias_suggestions]

admin.site.register(AliasLanguage, SuggestionAdmin)
admin.site.register(AliasAbstractDocument, SuggestionAdmin)
admin.site.register(AliasAuthor, SuggestionAdmin)
admin.site.register(AliasFileFormat, SuggestionAdmin)