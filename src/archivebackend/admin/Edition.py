import operator
from django import forms
from archivebackend.admin.AbstractAdmin import RemoteAdminView
from django import forms
from archivebackend.admin.AbstractAdmin import RemoteAdminView
from archivebackend.models import Edition, existanceType
from functools import reduce


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
    readonly_fields = ["last_file_update", "file_url", "original_authors", "from_remote"]

    def get_readonly_fields(self, request, obj=None):
        if obj is not None:
            if obj.existance_type != existanceType.LOCAL: # Make all fields readonly if the edition is not local
                return self.fields
        return super().get_readonly_fields(request, obj)

    # def save_model(self, request, obj, form, change):
    #     self.clean(form)
    #     super().save_model(request, obj, form, change)

    # def clean(self, form):
    #     """Ensure no authors are duplicated in either the original authors list or the additional authors list"""
    #     data = form.cleaned_data
    #     editionAuthors = data.get("edition_of").authors.all()
    #     additionalAuthors = data.get("additional_authors")
    #     originalAuthorsAliases = set(flatten([x.allAliases() for x in editionAuthors]))
    #     additionalAuthorsAliases = flatten([x.allAliases() for x in additionalAuthors])
    #     # If the set of aliases is the same length as the list, then there are no mutually aliased items in the list
    #     isUnique = len(set(additionalAuthorsAliases)) == len(additionalAuthorsAliases)
    #     InOriginal = any([extraAuthor in originalAuthorsAliases for extraAuthor in additionalAuthors])
    #     if not isUnique or InOriginal:
    #         raise forms.ValidationError("Some authors are already in the original authors list or are duplicated in the additional authors list")
        
