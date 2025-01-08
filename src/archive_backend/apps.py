import sys
from django.apps import AppConfig


class ArchiveBackendConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'archive_backend'

    def ready(self):
        import archive_backend.signals
        from archive_backend.generation.default_generation_filters import always, for_backups, if_no_revision_younger_than
        from archive_backend.generation.generation_registries import revision_generation_functions
        revision_generation_functions.register('always', always)
        revision_generation_functions.register('for backuprevisions', for_backups)
        revision_generation_functions.register('if no revision newer than config:<previous_revision_age> (string)', if_no_revision_younger_than)