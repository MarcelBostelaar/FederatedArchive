from datetime import datetime, timedelta
from archive_backend.jobs.util import getObjectListOnlySuccesfull
from archive_backend.models import Edition
from django_q.tasks import async_task
from django_q.tasks import schedule

def makelogentry(message):
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + message + "\n"

def download_latest_revision_for_editions(editionIds, attempts=0, log=""):
    # editions = getObjectListOnlySuccesfull(Edition, editionIds)
    print("!!!!!!!!!!!!!!!!!!!!!!!!Downloading latest revision for editions: ", editionIds)
    failure=True
    if failure:
        if attempts > 3:
            raise Exception("Failed to download latest revision for editions: ", editionIds, "Log: ", log)
        schedule('archive_backend.jobs.download_latest_revision_for_editions', editionIds, attempts=attempts+1, 
                   log=log + makelogentry("Failed"), 
                   name="Download latest revision for editions: " + str(editionIds),
                   schedule_type = "O", next_run = datetime.now() + timedelta(seconds=15))
        
        # Request latest revision from API endpoint
        # If cant connect, increase Attempts
        # If Attempts > 3, set status to failed
        # Create new revision in db based on info from API