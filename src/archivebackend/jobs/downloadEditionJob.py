from dataclasses import dataclass, field
from archivebackend.jobs.abstractJob import AbstractJobData
from archivebackend.models import Edition
from archivebackend.models.Job import JobStatus

@dataclass
class DownloadLatestRevisionJob(AbstractJobData):
    _EditionVal: Edition = field(init=False, metadata={"exclude": True})
    _editionID: str
    JobType: str = "DownloadLatestRevisionJob"

    @property
    def EditionVal(self):
        return self._EditionVal

    @EditionVal.setter
    def EditionVal(self, value):
        self._EditionVal = value
        self._editionID = value.id

    def __post_init__(self):
        super().__post_init__()
        
        if Edition.objects.filter(id=self._editionID).count() == 1:
            self.EditionVal = Edition.objects.filter(pk = self._editionID).first()
            return
        
        self.DatabaseJob.error_message += "Can't find edition with ID " + self._editionID + ".\n"
        self.DatabaseJob.status = JobStatus.FAILED
