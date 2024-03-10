from django.apps import AppConfig

from archivebackend.autogeneration import load_plugins


class ArchivebackendConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'archivebackend'

    def ready(self):
        load_plugins()