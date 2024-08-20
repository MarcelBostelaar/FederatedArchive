from django import forms
from archivebackend.admin.AbstractAdmin import RemoteAdminView
from django import forms
from archivebackend.admin.AbstractAdmin import RemoteAdminView
from archivebackend.models import Edition, existanceType


class EditionAdmin(RemoteAdminView):
    def original_authors(self, obj: Edition):
        # Calculate the desired information based on the model object (obj)
        # Return the calculated information as a string
        return ", ".join([x.fallback_name for x in obj.edition_of.authors.all()])
    
    def authors(self, obj: Edition):
        # Calculate the desired information based on the model object (obj)
        # Return the calculated information as a string
        return ", ".join([x.fallback_name for x in obj.edition_of.authors.all()] + [x.fallback_name for x in obj.additional_authors.all()])

    fields = ["title", "description", "from_remote", "original_authors", "additional_authors", "language", "existance_type", "edition_of", "publication_date", "last_file_update", "file_url"]
    autocomplete_fields = ["additional_authors"]
    list_display = ["title", "authors", "language", "existance_type", "edition_of"]
    readonly_fields = ["last_file_update", "file_url", "original_authors"]

    def get_readonly_fields(self, request, obj=None):
        if obj is not None:
            if obj.existance_type != existanceType.LOCAL: # Make all fields readonly if the edition is not local
                return self.fields
        return super().get_readonly_fields(request, obj)