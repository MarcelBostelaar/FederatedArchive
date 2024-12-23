import django
from django.core.management.base import BaseCommand

import os

class Command(BaseCommand):
    help = 'Deletes old migrations and generates new ones, migrates, creates superuser user: "admin" password "admin", and populates db with dummy data'

    def add_arguments(self , parser):
        parser.add_argument('--nodata', action='store_true')
        parser.add_argument('--nojobqueing', action='store_true')

    def handle(self, *args, **kwargs):
        migrations_files = []
        for root, dirs, files in os.walk('./src'):
            if 'migrations' in dirs:
                migrations_folder = os.path.join(root, 'migrations')
                for file in os.listdir(migrations_folder):
                    migrations_files.append(os.path.join(migrations_folder, file))

        filters = [
            "remote_peer_initial",
            "remote_peer_self_creation",
            "lock_own_remote_peer",
            "__init__",
            "__pycache__"
        ]

        for file in migrations_files:
            skip = False
            for filter in filters:
                if filter in file:
                    skip = True
                    continue
            if not skip:
                os.remove(file)
            
        if os.path.exists('./src/db.sqlite3'):
            os.remove('./src/db.sqlite3')

        django.core.management.call_command("makemigrations")
        django.core.management.call_command("migrate")

        os.environ.setdefault("DJANGO_SUPERUSER_PASSWORD", "admin")
        django.core.management.call_command("createsuperuser", "--noinput", "--username", "admin", "--email", "admin@admin.admin")
        if not kwargs.get('nodata'):
            if kwargs.get('nojobqueing'):
                django.core.management.call_command("generate_dummy_data", "--nojobqueing")
            else:
                django.core.management.call_command("generate_dummy_data", )