from archivebackend.jobs.abstractJob import AbstractJob, UUIDType
from archivebackend.models import Edition



class DownloadLatestRevisionJob(AbstractJob):
    Edition : UUIDType(Edition) # type: ignore
    JobType: str = "DownloadLatestRevisionJob"
    Attempts: int = 0

    def execute(self):
        pass
        # Request latest revision from API endpoint
        # If cant connect, increase Attempts
        # If Attempts > 3, set status to failed
        # Create new revision in db based on info from API