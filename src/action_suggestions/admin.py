from django.contrib import admin

from .models import *

# Register your models here.

admin.site.register(AliasLanguage)
admin.site.register(AliasAbstractDocument)
admin.site.register(AliasAuthor)
admin.site.register(AliasFileFormat)