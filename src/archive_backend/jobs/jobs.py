from archive_backend.jobs.util import getObjectListOnlySuccesfull
from archive_backend.models import Edition

from archive_backend.models.remote_peer import RemotePeer
from archive_backend.models.revision_file_models import Revision

def download_latest_revision_for_editions(editionIds):
    """Downloads the latest revision (and milestones) including files for an edition from a remote"""
    editions = getObjectListOnlySuccesfull(Edition, editionIds)
    #TODO implement

def generate_revisions(revisionIds):
    """Generates a revision from a parent revision"""
    revisions = getObjectListOnlySuccesfull(Revision, [revisionIds])
    #TODO implement

def download_update_everything_but_revisions(peerIds):
    """Downloads and updates all items from a peer, except revisions and files"""
    remotes = getObjectListOnlySuccesfull(RemotePeer, [peerIds])
    #dont forget all the through tables
    #update/set whether or not to mirror files. Signals will handle the rest
    #TODO implement