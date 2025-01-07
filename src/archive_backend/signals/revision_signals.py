from django.db.models.signals import post_save
from django.dispatch import receiver
from archive_backend.api.trigger_request import trigger_requestable
from archive_backend.models import *
from archive_backend.signals.edition_signals import local_requestable_generation_revision_check

from .util import (post_save_change_in_values, post_save_is_local_model,
                   post_save_new_item, post_save_new_values, post_save_new_values_NOTEQUALS_OR)

#New revisions

@receiver(post_save, sender=Revision)
@post_save_new_item()
@post_save_new_values(status=RevisionStatus.ONDISKPUBLISHED)
def NewOndiskRevision(sender = None, instance = None, *args, **kwargs):
    revision_published_event(instance)

@receiver(post_save, sender=Revision)
@post_save_new_item()
@post_save_new_values(status=RevisionStatus.REQUESTABLE)
@post_save_is_local_model(True)
def NewLocalGeneratingRequestable(sender = None, instance = None, *args, **kwargs):
    if instance.belongs_to.generation_config.automatically_regenerate:
        trigger_requestable(instance)

@receiver(post_save, sender=Revision)
@post_save_new_item()
@post_save_new_values(status=RevisionStatus.REQUESTABLE)
@post_save_is_local_model(False)
def NewRemoteRequestable(sender = None, instance = None, *args, **kwargs):
    remote_revision_requestable_check(instance)

#State changes

@receiver(post_save, sender=Revision)
@post_save_new_values(status=RevisionStatus.ONDISKPUBLISHED)
@post_save_change_in_values("status")
def RevisionPublished(sender = None, instance = None, *args, **kwargs):
    revision_published_event(instance)

@receiver(post_save, sender=Revision)
@post_save_new_values(status=RevisionStatus.REQUESTABLE)
@post_save_is_local_model(True)
@post_save_change_in_values("status")
def LocalRevisionRequestable(sender = None, instance = None, *args, **kwargs):
    if revision.belongs_to.generation_config.automatically_regenerate:
        trigger_requestable(revision)

@receiver(post_save, sender=Revision)
@post_save_new_values(status=RevisionStatus.REQUESTABLE)
@post_save_change_in_values("status")
@post_save_is_local_model(False)
def RemoteRevisionRequestable(sender = None, instance = None, *args, **kwargs):
    remote_revision_requestable_check(instance)

@receiver(post_save, sender=Revision)
@post_save_change_in_values("status")
def status_change(sender = None, instance = None, *args, **kwargs):
    for file in instance.files.all():
        file.fix_file()

# Supporting functions

def remote_revision_requestable_check(revision: Revision):
    """Triggers the request (to download it to this server) if the revision is remote and has mirror files"""
    if revision.from_remote.mirror_files:
        trigger_requestable(revision)

def revision_published_event(revision: Revision):
    #deleting non backup versions
    parent_edition = revision.belongs_to
    siblings = parent_edition.revisions.exclude(is_backup = True).exclude(id = revision.id)
    for sibling in siblings:
        sibling.delete()
    for i in parent_edition.generation_dependencies.all():
        local_requestable_generation_revision_check(i)

