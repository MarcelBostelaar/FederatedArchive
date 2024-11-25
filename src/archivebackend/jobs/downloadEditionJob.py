from archivebackend.jobs.abstractJob import AbstractJobData, UUIDType
from archivebackend.models import Edition

class DownloadLatestRevisionJob(AbstractJobData):
    Edition : UUIDType(Edition) # type: ignore
    JobType: str = "DownloadLatestRevisionJob"
