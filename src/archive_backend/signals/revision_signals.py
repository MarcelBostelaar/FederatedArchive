from django.db.models.signals import post_save
from django.dispatch import receiver
from archive_backend import api
from archive_backend.api.apiviews import ArchiveFileViews
from archive_backend.api.serializers import ArchiveFileSerializer
from archive_backend.generation.generation_handler import startGeneration
from archive_backend.jobs.job_exceptions import BaseJobRescheduleException
from archive_backend.models import *
from archive_backend.signals.edition_signals import local_requestable_generation_revision_check
from archive_backend.utils.small import get_json_from_remote, ping_url

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
    local_revision_became_requestable(instance)

@receiver(post_save, sender=Revision)
@post_save_new_values(status=RevisionStatus.REQUESTABLE)
@post_save_change_in_values("status")
@post_save_new_values_NOTEQUALS_OR(from_remote=RemotePeer.getLocalSite())
def RemoteRevisionRequestable(sender = None, instance = None, *args, **kwargs):
    remote_revision_became_requestable(instance)

# Supporting functions

def local_revision_became_requestable(revision: Revision):
    if revision.belongs_to.generation_config.automatically_regenerate:
        trigger_requestable(revision)

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

def trigger_requestable(revision: Revision):
    match revision.status:
        case RevisionStatus.UNFINISHED:
            raise Exception("Cannot trigger requestable for an unfinished revision")
        case RevisionStatus.ONDISKPUBLISHED:
            return
        case RevisionStatus.JOBSCHEDULED:
            return
        case RevisionStatus.REMOTEJOBSCHEDULED:
            return
        case RevisionStatus.REMOTEREQUESTABLE:
            trigger_remote_requestable(revision)
            return
        case RevisionStatus.REQUESTABLE:
            match [revision.generated_from, revision.from_remote.is_this_site]:
                case [None, True]:
                    raise Exception("Local requestable revision has no generation source")
                case [None, False]:
                    full_download_remote_revision(revision)
                    return
                case [_, True]:
                    startGeneration(revision)
                    return
                case [_, False]:
                    raise Exception("Remote requestable revision has a generation source")

#TODO jobify
def trigger_remote_requestable(revision: Revision):
    code = ping_url(api.getTriggerRequestUrl(revision))
    if code >= 500:
        raise BaseJobRescheduleException(10, "Remote server returned 500-599 error.")
    if code >= 400:
        raise Exception(f"Remote server returned {code} error")
    if code >= 300:
        raise Exception(10, "Remote server returned 300-399 error")
    revision.status = RevisionStatus.REMOTEJOBSCHEDULED
    revision.save()

#TODO jobify
def full_download_remote_revision(revision: Revision):
    revision.status = RevisionStatus.JOBSCHEDULED
    revision.save()
    url = ArchiveFileViews.get_list_url(related_revision=revision.id, on_site=revision.from_remote.site_adress)
    data = get_json_from_remote(url)
    for item in data:
        ArchiveFileSerializer.create_or_update_from_remote_data(item, revision.from_remote.site_adress)
