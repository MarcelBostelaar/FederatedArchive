from archivebackend.admin.AbstractAdmin import RemoteAdminView


class EditionAdmin(RemoteAdminView):
    autocomplete_fields = ["additional_authors"]
    readonly_fields = ["last_file_update", "file_url"]
    pass