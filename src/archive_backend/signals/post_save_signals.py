from django.db.models.signals import post_save
from django.dispatch import receiver
from django_q.tasks import async_task

from archive_backend.jobs.util import pkStringList
from archive_backend.models import *
from archive_backend.signals.shared_funtions import (
    CreateLocalRequestableRevision, PostNewRevisionEvent)

from .util import (post_save_change_in_any, post_save_change_in_values,
                   post_save_new_item, post_save_new_values,
                   post_save_new_values_NOTEQUALS_OR)

##RemotePeer

def ScheduleDownloadAllEditionsForPeer(peer):
    async_task('archive_backend.jobs.download_update_everything_but_revisions', pkStringList([peer]), 
               task_name=("Downloading from peer: " + str(peer.site_name))[:100])

@receiver(post_save, sender=RemotePeer)
@post_save_change_in_values("mirror_files")
@post_save_new_values(mirror_files = True)
def RemotePeerStartMirroring(sender = None, instance = None, *args, **kwargs):
    ScheduleDownloadAllEditionsForPeer(instance)

@receiver(post_save, sender=RemotePeer)
@post_save_new_values(mirror_files = True)
@post_save_new_item()
def RemotePeerStartMirroring(sender = None, instance = None, *args, **kwargs):
    ScheduleDownloadAllEditionsForPeer(instance)


##Edition

@receiver(post_save, sender=Edition)
@post_save_change_in_any("generation_config", "actively_generated_from")
@post_save_new_values_NOTEQUALS_OR(generation_config = None, actively_generated_from = None)
def AutogenConfigChanged(sender = None, instance = None, *args, **kwargs):
    CreateLocalRequestableRevision(instance)

#New editions

#Generated
@receiver(post_save, sender=Edition)
@post_save_new_item()
@post_save_new_values_NOTEQUALS_OR(generation_config = None, actively_generated_from = None)
def NewGeneratedEdition(sender = None, instance = None, *args, **kwargs):
    #Only fires on local editions, because
    #remote editions can not have generation configurations
    CreateLocalRequestableRevision(instance)

#Regular
@receiver(post_save, sender=Edition)
@post_save_new_item()
@post_save_new_values(generation_config = None, actively_generated_from = None)
def NewRegularEdition(sender = None, instance = None, *args, **kwargs):
    if instance.from_remote.is_this_site:
        #Ensure empty starting revision to prevent autogeneration errors
        Revision.objects.create(belongs_to = instance, status = RevisionStatus.ONDISKPUBLISHED).save()
    #Remote editions should not have local revisions


##Revision

@receiver(post_save, sender=Revision)
@post_save_new_item()
def NewRevisionEvent(sender = None, instance = None, *args, **kwargs):
    PostNewRevisionEvent(instance)

@receiver(post_save, sender=Revision)
@post_save_change_in_values("status")
@post_save_new_values(status=RevisionStatus.ONDISKPUBLISHED)
def RevisionPublished(sender = None, instance = None, *args, **kwargs):
    # Make a new generated revision for all dependencies
    for dependency in instance.belongs_to.generation_dependencies.all():
        CreateLocalRequestableRevision(dependency) 

    # Delete all non-backup revisions except the latest one
    for oldRevision in instance.belongs_to.revisions.exclude(is_backup = True).order_by("-date")[1:]:
        oldRevision.delete() 

##GenerationConfig
@receiver(post_save, sender=GenerationConfig)
@post_save_change_in_values("script_name", "automatically_regenerate", 
                            "source_file_format", "target_file_format", 
                            "config_json")
def GenerationConfigChanged(sender = None, instance = None, *args, **kwargs):
    for edition in instance.editions:
        CreateLocalRequestableRevision(edition)

