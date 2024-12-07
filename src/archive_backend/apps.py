import sys
from django.apps import AppConfig




class ArchiveBackendConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'archive_backend'

    def ready(self):
        import archive_backend.signals
        from archive_backend.generation import register_generator, registered
        from archive_backend.generation.example_generator import text_all_caps
        register_generator("allcapsnobreaks", text_all_caps)
        test = registered
        i = 10