from .util import tryConvertToDataclass
from .downloadEditionJob import *

jobs = []

def jobConverter(data):
    """Converts a dictionary to a Job object."""
    for job in jobs:
        converted = tryConvertToDataclass(data, job)
        if converted is not None:
            return converted
    raise ValueError(f"Could not convert {data} to a Job object. Missing job class?")