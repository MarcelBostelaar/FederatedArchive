from django.apps import AppConfig



class ArchivebackendConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'archivebackend'

    def ready(self):
        from archivebackend.autogeneration import load_plugins
        load_plugins("plugins")