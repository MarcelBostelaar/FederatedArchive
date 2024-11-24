from dataclasses import dataclass
from archivebackend.jobs.abstractJob import AbstractJobData
from archivebackend.models import Edition

editionIDKey = "editionID"

@dataclass
class DownloadLatestRevisionJob(AbstractJobData):
    EditionVal: Edition
    JobType = "DownloadEdition"

    def __init__(self):
        super().__init__()

    def deserialise(self, valueDict, databaseJob):
        super.deserialise(valueDict, databaseJob)
        self.DatabaseJob = databaseJob
        self.EditionVal = Edition.objects.get(valueDict[editionIDKey])
        return self

    def __childSerialise(self, obj):
        obj[editionIDKey] = Edition.id
        return obj
