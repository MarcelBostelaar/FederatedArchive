from archivebackend.admin.AbstractAdmin import RemoteAdminView


class EditionAdmin(RemoteAdminView):
    autocomplete_fields = ["additional_authors"]
    pass