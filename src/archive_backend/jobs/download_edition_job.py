from archive_backend.models import Edition
from job_manager.abstract_job import AbstractJob, UUIDListType


class DownloadLatestRevisionForEditionsJob(AbstractJob):
    Editions : UUIDListType(Edition) # type: ignore
    JobType: str = "DownloadLatestRevisionForEditions"
    Attempts: int = 0

    def execute(self):
        pass
        # Request latest revision from API endpoint
        # If cant connect, increase Attempts
        # If Attempts > 3, set status to failed
        # Create new revision in db based on info from API