from archive_backend.jobs.util import getObjectListOnlySuccesfull
from archive_backend.models import Edition
from django_q.tasks import async_task
from django_q.tasks import schedule

from archive_backend.models.generation_config import AutoGeneration
from archive_backend.models.revision_file_models import File, Revision

def download_latest_revision_for_editions(editionIds):
    """Downloads the latest revision (and milestones) including files for an edition from a remote"""
    editions = getObjectListOnlySuccesfull(Edition, editionIds)
    #TODO implement

def delete_old_revisions(editionIds):
    editions = getObjectListOnlySuccesfull(Edition, editionIds)
    #TODO implement

def generate_revisions(revisionIds):
    """Generates a revision from a parent revision"""
    revisions = getObjectListOnlySuccesfull(Revision, [revisionIds])
    #TODO implement