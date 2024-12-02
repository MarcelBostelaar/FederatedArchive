from datetime import datetime, timedelta
from archive_backend.jobs.util import getObjectListOnlySuccesfull
from archive_backend.models import Edition
from django_q.tasks import async_task
from django_q.tasks import schedule

def makelogentry(message):
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + message + "\n"

def download_latest_revision_for_editions(editionIds):
    editions = getObjectListOnlySuccesfull(Edition, editionIds)
    #TODO implement

def remove_local_files_for(editionIds):
    editions = getObjectListOnlySuccesfull(Edition, editionIds)
    #TODO implement