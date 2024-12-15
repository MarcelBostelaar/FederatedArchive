from uuid import UUID
import warnings

import requests
from archive_backend.generation import startGeneration
from archive_backend.jobs.util import getObjectListOnlySuccesfull, getObjectOrNone, pkStringList
from django_q.tasks import async_task
from archive_backend.models import *
from archive_backend.api import *
from datetime import datetime

update_order = [
        RemotePeer,
        Language,
        FileFormat,
        Author,
        AuthorDescriptionTranslation,
        AbstractDocument,
        AbstractDocumentDescriptionTranslation,
        Edition
] #Revision and ArchiveFile are not included because they are handled by signals based on server settings

def update_download_all(from_remote: RemotePeer):
    last_checkin = from_remote.last_checkin
    datetime_at_job_time = datetime.now()

    for model in update_order:
        ViewContainer = ViewContainerRegistry.get(model)
        url = ViewContainer.get_list_url(on_site=from_remote.site_adress, updated_after=last_checkin)
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        for item in data:
            #Use this method to
            # 1 Ensure possible table-self references are handled correctly (will send an additional request for each item), as well as catching any race conditions (item was updated in remote to reference new item made after sync of that table)
            # 2 Fire signals and save functions (which may contain validation logic and schedule other jobs)
            # While this may be slower than bulk create, jobs are not expected to be frequent and are handled by the background process
            SerializerRegistry.get(model).create_or_update_from_remote_data(item, from_remote.site_adress)
        if ViewContainer.is_alias_container():
            ViewContainer.download_aliases(from_remote.site_adress)

    from_remote.last_checkin = datetime_at_job_time
    from_remote.save()

def download_latest_revision_for_editions(editionIds):
    """Downloads the latest revision (and milestones) including files for an edition from a remote"""
    editions = getObjectListOnlySuccesfull(Edition, editionIds)
    warnings.warn("Executed download_latest_revision_for_editions job. This job is not implemented yet")
    #TODO remove old requestable revisions that are created on this site
    #TODO implement

def download_revisions(revisionIds):
    """Downloads a revision from a remote"""
    revisions = getObjectListOnlySuccesfull(Revision, revisionIds)
    warnings.warn("Executed download_revisions job. This job is not implemented yet")
    #TODO implement

def download_update_everything_but_revisions(peerIds):
    """Downloads and updates all items from a peer, except revisions and files"""
    remotes = getObjectListOnlySuccesfull(RemotePeer, peerIds)
    warnings.warn("Executed download_update_everything_but_revisions job. This job is not implemented yet")
    #dont forget all the through tables
    #update/set whether or not to mirror files. Signals will handle the rest
    #TODO implement

def is_remote_revision_downloadable(revisionId):
    raise NotImplementedError("Not implemented yet")

def request_remote_requestable(revisionId):
    """Requests a remote revision"""
    revision = getObjectOrNone(Revision, revisionId)
    warnings.warn("Executed request_remote_requestable job. This job is not implemented yet")
    if revision is None:
        raise "Could not find revision with id " + str(revisionId)
    if is_remote_revision_downloadable(revision):
        revision.status = RevisionStatus.JOBSCHEDULED
        revision.save()
        download_revisions([revisionId])
    #TODO implement sending request
    