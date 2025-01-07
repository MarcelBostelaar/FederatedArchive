from django.db.models.signals import post_save
from django.dispatch import receiver
from archive_backend.models import *
from archive_backend.signals.util import post_save_change_in_values

@receiver(post_save, sender=FileFormat)
@post_save_change_in_values("format_id")
def status_change(sender = None, instance = None, *args, **kwargs):
    for file in instance.archive_files.all():
        file.fix_file()