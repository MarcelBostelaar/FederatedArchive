jobs = {}

def JobsRegistry(jobName, cls):
    """Registers a job class for conversion from json."""
    if jobName in jobs:
        raise ValueError(f"Job {jobName} already registered.")
    jobs[jobName] = cls

def jobConverter(data):
    """Converts a dictionary to a Job object."""
    name = data["JobType"]
    if name not in jobs:
        raise ValueError(f"Job {name} not registered.")
    return jobs[name].parse_object(data)