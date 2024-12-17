from uuid import UUID
import warnings

import requests
from archive_backend.generation import startGeneration
from .syncing_util import download_revision, get_json_from_remote, get_remote_revision_state, trigger_remote_requestable, update_download_all
from .util import getObjectListOnlySuccesfull, getObjectOrNone, pkStringList
from django_q.tasks import async_task
from archive_backend.models import *
from archive_backend.api import *
from datetime import datetime
from archive_backend.signals.revision_events import schedule_download_remote_revision


#Used in _downloadRemoteRevision in revision_events
def download_revision_job(revisionID):
    """Downloads a revision"""
    revision = getObjectOrNone(Revision, revisionID)
    if revision is None:
        return
    return download_revision(revision)



#Used in ScheduleDownloadAllForPeer in post_save_signals
def download_update_everything_but_revisions_job(peerIds):
    """Downloads and updates all items from a peer, except revisions and files"""
    remotes = getObjectListOnlySuccesfull(RemotePeer, peerIds)
    for i in remotes:
        update_download_all(i)

#Used in _requestRemoteRequestable in revision_events
def trigger_remote_requestable_job(revisionId):
    """Requests a remote revision"""
    revision = getObjectOrNone(Revision, revisionId)
    warnings.warn("Executed trigger_remote_requestable_job job. This job is not implemented yet")
    if revision is None:
        raise "Could not find revision with id " + str(revisionId)
    remote_revision_state = get_remote_revision_state(revision)
    match remote_revision_state:
        case RevisionStatus.ONDISKPUBLISHED:
            revision.status = RevisionStatus.REQUESTABLE
            revision.save()
            return schedule_download_remote_revision(revision)
        case RevisionStatus.REQUESTABLE:
            trigger_remote_requestable(revision)
            return
        case RevisionStatus.REMOTEREQUESTABLE:
            trigger_remote_requestable(revision)
            return
        case RevisionStatus.JOBSCHEDULED:
            #Already triggered
            return
        case RevisionStatus.REMOTEJOBSCHEDULED:
            #Already triggered
            return
        case _:
            raise "Invalid remote revision state: " + str(remote_revision_state)
    