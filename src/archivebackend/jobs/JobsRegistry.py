from archivebackend.jobs.abstractJob import AbstractJob


jobs = {}

def JobsRegistry(cls: AbstractJob):
    """Registers a job class for conversion from json."""
    if not isinstance(cls.JobType, str):
        raise ValueError("JobType must be a string.")
    if cls.JobType in jobs:
        raise ValueError(f"Job {cls.JobType} already registered.")
    jobs[cls.JobType] = cls

def jobConverter(data):
    """Converts a dictionary to a Job object."""
    name = data["JobType"]
    if name not in jobs:
        raise ValueError(f"Job {name} not registered.")
    return jobs[name].parse_object(data)