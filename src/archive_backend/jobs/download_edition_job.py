from archive_backend.jobs.util import getObjectListOnlySuccesfull
from archive_backend.models import Edition


def download_latest_revision_for_editions(editionIds):
    editions = getObjectListOnlySuccesfull(Edition, editionIds)
    print("!!!!!!!!!!!!!!!!!!!!!!!!Downloading latest revision for editions: ", editionIds)
        # Request latest revision from API endpoint
        # If cant connect, increase Attempts
        # If Attempts > 3, set status to failed
        # Create new revision in db based on info from API