from django.db.models.signals import post_save
from django.dispatch import receiver

from archive_backend.api.download_all import update_download_all
from archive_backend.models import RemotePeer
from .util import (post_save_change_in_values,
                   post_save_new_item, post_save_new_values)

@receiver(post_save, sender=RemotePeer)
@post_save_change_in_values("mirror_files")
@post_save_new_values(mirror_files = True)
def RemotePeerStartMirroring(sender = None, instance = None, *args, **kwargs):
    update_download_all(instance)

@receiver(post_save, sender=RemotePeer)
@post_save_new_values(mirror_files = True)
@post_save_new_item()
def RemotePeerStartMirroring(sender = None, instance = None, *args, **kwargs):
    update_download_all(instance)