import sys
from django.apps import AppConfig

class ArchiveBackendConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'archive_backend'

    def ready(self):
        import archive_backend.signals
        from archive_backend.generation.default_generation_filters import always_true_filter, on_backups_filter, if_no_revision_younger_than_filter
        from archive_backend.generation.generation_registries import make_new_generated_revision_filters
        make_new_generated_revision_filters.register('always', always_true_filter)
        make_new_generated_revision_filters.register('for backuprevisions', on_backups_filter)
        make_new_generated_revision_filters.register('if no revision newer than config:<previous_revision_age> (string)', if_no_revision_younger_than_filter)