import sys
from django.apps import AppConfig



class ArchiveBackendConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'archive_backend'

    def ready(self):
        import archive_backend.signals
        #Prevent crashing of program during migrations due to this initialisation code accesing the database tables that may not exist yet
        if not ('makemigrations' in sys.argv or 'migrate' in sys.argv):
            pass