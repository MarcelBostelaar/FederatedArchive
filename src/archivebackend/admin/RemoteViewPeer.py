from archivebackend.admin.AbstractAdmin import RemoteAdminView


class RemotePeerView(RemoteAdminView):
    exclude = ["is_this_site"]
    readonly_fields = ('last_checkin',)
    list_display = ('site_name', 'site_adress', 'mirror_files', 'peers_of_peer', 'is_this_site', 'from_remote')
    list_filter = ('mirror_files', 'peers_of_peer', 'from_remote', 'is_this_site')
