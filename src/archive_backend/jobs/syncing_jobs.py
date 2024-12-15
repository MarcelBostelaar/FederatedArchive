from archive_backend.generation import startGeneration
from archive_backend.jobs.util import getObjectListOnlySuccesfull, getObjectOrNone, pkStringList
from django_q.tasks import async_task
from archive_backend.models import Revision, RevisionStatus, RemotePeer, Edition, Language
from archive_backend.api import *

def download_remote_peer(id, from_address):
    SerializerRegistry.get(RemotePeer).download_from_remote_site(id, from_address)
def download_langauge(id, from_address):
    result = SerializerRegistry.get(Language).download_from_remote_site(id, from_address)
    i = 10
def download_file_format(id, from_address):
    raise NotImplementedError("Not implemented")
def download_author(id, from_address):
    raise NotImplementedError("Not implemented")
def download_author_description_translation(id, from_address):
    raise NotImplementedError("Not implemented")
def download_abstract_document(id, from_address):
    raise NotImplementedError("Not implemented")
def download_abstract_document_description_translation(id, from_address):
    raise NotImplementedError("Not implemented")
def download_edition(id, from_address):
    raise NotImplementedError("Not implemented")
def download_revision(id, from_address):
    raise NotImplementedError("Not implemented")
def download_archive_file(id, from_address):
    raise NotImplementedError("Not implemented")



def download_latest_revision_for_editions(editionIds):
    """Downloads the latest revision (and milestones) including files for an edition from a remote"""
    editions = getObjectListOnlySuccesfull(Edition, editionIds)
    #TODO remove old requestable revisions that are created on this site
    #TODO implement

def download_revisions(revisionIds):
    """Downloads a revision from a remote"""
    revisions = getObjectListOnlySuccesfull(Revision, revisionIds)
    #TODO implement

def download_update_everything_but_revisions(peerIds):
    """Downloads and updates all items from a peer, except revisions and files"""
    remotes = getObjectListOnlySuccesfull(RemotePeer, peerIds)
    #dont forget all the through tables
    #update/set whether or not to mirror files. Signals will handle the rest
    #TODO implement

def is_remote_revision_downloadable(revisionId):
    raise NotImplementedError("Not implemented yet")



def request_remote_requestable(revisionId):
    """Requests a remote revision"""
    revision = getObjectOrNone(Revision, revisionId)
    if revision is None:
        raise "Could not find revision with id " + str(revisionId)
    if is_remote_revision_downloadable(revision):
        revision.status = RevisionStatus.JOBSCHEDULED
        revision.save()
        download_revisions([revisionId])
    #TODO implement sending request
    