from archive_backend.generation import startGeneration
from archive_backend.jobs.util import getObjectListOnlySuccesfull, getObjectOrNone, pkStringList
from django_q.tasks import async_task

from archive_backend.models import Revision

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