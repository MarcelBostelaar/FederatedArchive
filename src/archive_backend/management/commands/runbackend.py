
import django
from django.core.management.base import BaseCommand
from archive_backend import config
from archive_backend.utils.small import flatten

#from https://stackoverflow.com/a/34993964/7183662
class Command(BaseCommand):
    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument('--nojobqueing', action='store_true')

    def handle(self, *args, **kwargs):
        config.do_job_queueing = not kwargs['nojobqueing']
        kwargs.pop('nojobqueing')
        django.core.management.call_command("runserver", *args, **kwargs)
