from django.db.models.signals import post_save
from django.dispatch import receiver
from archive_backend.api.trigger_request import trigger_requestable
from archive_backend.models import *
from archive_backend.signals.edition_signals import local_requestable_generation_revision_check

from .util import (post_save_change_in_values,
                   post_save_new_item, post_save_new_values, post_save_new_values_NOTEQUALS_OR)

#New revisions

@receiver(post_save, sender=Revision)
@post_save_new_item()
@post_save_new_values(status=RevisionStatus.ONDISKPUBLISHED)
def NewOndiskRevision(sender = None, instance = None, *args, **kwargs):
    revision_published_event(instance)

@receiver(post_save, sender=Revision)
@post_save_new_item()
@post_save_new_values(status=RevisionStatus.REQUESTABLE, from_remote = RemotePeer.getLocalSite())
def NewLocalGeneratingRequestable(sender = None, instance = None, *args, **kwargs):
    if instance.belongs_to.generation_config.automatically_regenerate:
        trigger_requestable(instance)

@receiver(post_save, sender=Revision)
@post_save_new_item()
@post_save_new_values(status=RevisionStatus.REQUESTABLE)
@post_save_new_values_NOTEQUALS_OR(from_remote=RemotePeer.getLocalSite())
def NewRemoteRequestable(sender = None, instance = None, *args, **kwargs):
    remote_revision_became_requestable(instance)

#State changes

@receiver(post_save, sender=Revision)
@post_save_new_values(status=RevisionStatus.ONDISKPUBLISHED)
@post_save_change_in_values("status")
def RevisionPublished(sender = None, instance = None, *args, **kwargs):
    revision_published_event(instance)

@receiver(post_save, sender=Revision)
@post_save_new_values(status=RevisionStatus.REQUESTABLE, from_remote=RemotePeer.getLocalSite())
@post_save_change_in_values("status")
def LocalRevisionRequestable(sender = None, instance = None, *args, **kwargs):
    if revision.belongs_to.generation_config.automatically_regenerate:
        trigger_requestable(revision)

@receiver(post_save, sender=Revision)
@post_save_new_values(status=RevisionStatus.REQUESTABLE)
@post_save_change_in_values("status")
@post_save_new_values_NOTEQUALS_OR(from_remote=RemotePeer.getLocalSite())
def RemoteRevisionRequestable(sender = None, instance = None, *args, **kwargs):
    remote_revision_became_requestable(instance)

# Supporting functions

def remote_revision_became_requestable(revision: Revision):
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

