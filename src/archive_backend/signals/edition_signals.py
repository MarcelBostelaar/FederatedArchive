from django.db.models.signals import post_save
from django.dispatch import receiver

from archive_backend.api import *
from archive_backend.jobs.job_decorator import jobify_model
from archive_backend.models import *
from archive_backend.generation import revision_generation_functions
from archive_backend.utils.small import HttpUtil

from .util import (post_save_change_in_any, 
                   post_save_new_item,
                   post_save_new_values_NOTEQUALS_OR, post_save_is_local_model)

#Changes to generation configs
@receiver(post_save, sender=Edition)
@post_save_change_in_any("generation_config_id", "actively_generated_from_id")
@post_save_new_values_NOTEQUALS_OR(generation_config = None, actively_generated_from = None)
def AutogenConfigChanged(sender = None, instance = None, *args, **kwargs):
    local_requestable_generation_revision_check(instance)

#New editions

#New Local Generated
@receiver(post_save, sender=Edition)
@post_save_new_item()
@post_save_new_values_NOTEQUALS_OR(generation_config = None, actively_generated_from = None)
@post_save_is_local_model(True)
def NewGeneratedEdition(sender = None, instance = None, *args, **kwargs):
    local_requestable_generation_revision_check(instance)

#New Remote
@receiver(post_save, sender=Edition)
@post_save_new_item()
@post_save_is_local_model(False)
def NewRemoteEdition(sender = None, instance = None, *args, **kwargs):
    create_requestables(instance)



#Supporting functions

@jobify_model("archive_backend.signals.edition_signals.create_requestable", Edition)
def create_requestables(edition: Edition):
    create_requestable_revisions_for_remote_backups(edition)
    create_requestable_revision_for_remote_latest(edition)


def local_requestable_generation_revision_check(edition: Edition):
    fun = revision_generation_functions.get(edition.generation_config.revision_generation_function)
    fun(edition)

@jobify_model("archive_backend.signals.edition_signals.create_requestable_revisions_for_remote_backups", Edition)  
def create_requestable_revisions_for_remote_backups(edition: Edition):
    url = RevisionViews.get_list_url(
        on_site = edition.from_remote.site_adress, 
        backups_only = True, 
        related_edition=edition.pk)
    data = HttpUtil().get_json_from_remote(url)
    for i in data:
        RevisionSerializer.create_or_update_from_remote_data(i, edition.from_remote.site_adress)

@jobify_model("archive_backend.signals.edition_signals.create_requestable_revision_for_remote_latest", Edition)
def create_requestable_revision_for_remote_latest(edition: Edition):
    url = RevisionViews.get_list_url(
        on_site = edition.from_remote.site_adress, 
        latest_only = True, 
        related_edition=edition.pk)
    data = HttpUtil().get_json_from_remote(url)
    if len(data) != 1:
        raise Exception(f"Remote returned {len(data)} revisions for request of latest revision for {edition.id} on remote site {edition.from_remote.site_name}")
    RevisionSerializer.create_or_update_from_remote_data(data[0], edition.from_remote.site_adress)
