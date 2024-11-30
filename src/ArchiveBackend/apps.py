import sys
from django.apps import AppConfig



class ArchivebackendConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ArchiveBackend'

    def ready(self):
        import ArchiveBackend.signals
        #Prevent crashing of program during migrations due to this initialisation code accesing the database tables that may not exist yet
        if not ('makemigrations' in sys.argv or 'migrate' in sys.argv):
            # from ArchiveBackend.autogeneration import load_plugins
            # load_plugins("plugins")
            #TODO temporarily disabled until plugin system works properly
            pass