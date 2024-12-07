from archive_backend.generation import startGeneration
from archive_backend.jobs.util import getObjectListOnlySuccesfull, getObjectOrNone, pkStringList
from archive_backend.models import Edition
from django_q.tasks import async_task

from archive_backend.models.remote_peer import RemotePeer
from archive_backend.models.revision_file_models import Revision

def download_latest_revision_for_editions(editionIds):
    """Downloads the latest revision (and milestones) including files for an edition from a remote"""
    editions = getObjectListOnlySuccesfull(Edition, editionIds)
    #TODO remove old requestable revisions that are created on this site
    #TODO implement

def download_revisions(revisionIds):
    """Downloads a revision from a remote"""
    revisions = getObjectListOnlySuccesfull(Revision, revisionIds)
    #TODO implement

def generate_single_revision(revisionId):
    """Generates a revision from a parent revision"""
    revision = getObjectOrNone(Revision, revisionId)
    if revision is None:
        raise "Could not find revision with id " + str(revisionId)
    startGeneration(revision)

def generate_revisions(revisionIds):
    """Generates a revision from a parent revision"""
    revisions = getObjectListOnlySuccesfull(Revision, revisionIds)
    for i in revisions:
        async_task("archive_backend.jobs.generate_single_revision", str(i.pk), task_name=("Generating revision " + str(i.pk))[:100])

def download_update_everything_but_revisions(peerIds):
    """Downloads and updates all items from a peer, except revisions and files"""
    remotes = getObjectListOnlySuccesfull(RemotePeer, peerIds)
    #dont forget all the through tables
    #update/set whether or not to mirror files. Signals will handle the rest
    #TODO implement