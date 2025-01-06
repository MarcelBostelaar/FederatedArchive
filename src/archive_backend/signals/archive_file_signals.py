from django.db.models.signals import post_save
from django.dispatch import receiver

from archive_backend.api import *
from archive_backend.models import *
from archive_backend.utils.small import HttpUtil

from .util import (post_save_new_item,
                   post_save_is_local_model)

@receiver(post_save, sender=ArchiveFile)
@post_save_new_item()
@post_save_is_local_model(False)
def NewRemoteFile(sender = None, instance = None, *args, **kwargs):
    #TODO call a jobified function so that individual file failure doesnt stop the whole process
    raise NotImplementedError("Remote files download")