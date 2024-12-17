from django.db.models.signals import post_save
from django.dispatch import receiver
from archive_backend.models import GenerationConfig
from archive_backend.signals.edition_signals import local_requestable_generation_revision_check

from .util import post_save_change_in_any

def GenerationChangeEvent(config):
    for edition in config.edition_set.all():
        local_requestable_generation_revision_check(edition)
    for i in config.previous_steps.all():
        GenerationChangeEvent(i)

@receiver(post_save, sender=GenerationConfig)
@post_save_change_in_any("registered_name", "automatically_regenerate", 
                            "config_json", "next_step")
def GenerationConfigChanged(sender = None, instance = None, *args, **kwargs):
    GenerationChangeEvent(instance)

