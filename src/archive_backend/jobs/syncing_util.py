
import warnings
import requests
from archive_backend.models import *
from archive_backend.api import *
from datetime import datetime

from archive_backend.utils.small import get_json_from_remote



def download_revision(revision: Revision):
    """Downloads a revision from a remote"""
    remote_status = get_remote_revision_state(revision)
    if remote_status != RevisionStatus.ONDISKPUBLISHED:
        raise Exception("Remote revision is not published")
    if revision.status != RevisionStatus.JOBSCHEDULED:
        raise Exception("Revision is not scheduled for download")
    url = ArchiveFileViews.get_list_url(related_revision=revision.id, on_site=revision.from_remote.site_adress)
    data = get_json_from_remote(url)
    for data in data:
        ArchiveFileSerializer.create_or_update_from_remote_data(data, revision.from_remote.site_adress)
    revision.status = RevisionStatus.ONDISKPUBLISHED
    revision.save()

def get_remote_revision_state(revision: Revision):
    data = get_json_from_remote(RevisionViews.get_detail_url(revision.id, on_site=revision.from_remote.site_adress))
    if data is {}:
        raise Exception("No remote revision found for this id: " + str(revision.id))
    status = RevisionStatus(data["status"])
    return status

def trigger_remote_requestable(revision: Revision):
    """Requests a remote revision"""
    warnings.warn("Executed trigger_remote_requestable. This is not implemented yet")
    raise NotImplementedError("Not implemented yet")
    revision.status = RevisionStatus.REMOTEJOBSCHEDULED
    revision.save()