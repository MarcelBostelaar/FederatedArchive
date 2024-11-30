

from .abstractJob import AbstractJob


jobs = {}

def JobsRegistry(cls: AbstractJob):
    """Registers a job class for conversion from json."""
    jobname = cls.model_fields["JobType"].default
    if not isinstance(jobname, str):
        raise ValueError("JobType must be a string.")
    if jobname in jobs:
        raise ValueError(f"Job {jobname} already registered.")
    jobs[jobname] = cls

def jobConverter(data):
    """Converts a dictionary to a Job object."""
    name = data["JobType"]
    if name not in jobs:
        raise ValueError(f"Job {name} not registered.")
    return jobs[name].parse_object(data)