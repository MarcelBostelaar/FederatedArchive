JobTypeKey = "JobType"

class AbstractJobData:
    JobType = None
    DatabaseJob = None

    def __init__(self, DatabaseJob):
        pass

    def deserialise(self, valueDict, databaseJob):
        self.DatabaseJob = databaseJob
        self.JobType = valueDict[JobTypeKey]
        return self

    def serialise(self):
        obj = {}
        obj[JobTypeKey] = self.JobType
        return self.__childSerialise(obj)

    def __childSerialise(self, obj):
        raise NotImplementedError("Job had not implemented child serialise method.")