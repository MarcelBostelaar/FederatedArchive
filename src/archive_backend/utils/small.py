from itertools import islice
from typing import Generator, Iterator, List
from typing import Generic, TypeVar

import requests

from archive_backend import config
from archive_backend.jobs.job_exceptions import JobRescheduleConnectionError, JobRescheduleConnectionTimeoutException


def flatten(x):
    return [item for sublist in x for item in sublist]

KEY = TypeVar('KEY')
VALUE = TypeVar('VALUE')

class registry(Generic[KEY, VALUE]):
    def __init__(self, registry_name_for_debugging: str = "unnamed"):
        self._registry: dict[KEY, VALUE] = {}
        self._name: str = registry_name_for_debugging

    def register(self, key: KEY, value: VALUE) -> None:
        if key in self._registry:
            raise ValueError(f"Duplicate registration of {key} in registry {self._name}")
        self._registry[key] = value

    def get(self, key: KEY) -> VALUE:
        if key not in self._registry:
            raise ValueError(f"Item {key} is not registered in registry {self._name}")
        return self._registry[key]
    
    def override(self, key: KEY, value: VALUE) -> None:
        if key not in self._registry:
            raise ValueError(f"Item {key} is not registered in registry {self._name}")
        self._registry[key] = value
 
class HttpUtil:
    """Util to perform http commands.
    
    Exists to easily mock and isolate the requests"""
    def get_json_from_remote(self, url: str):
        """Tries to fetch json from a server.
        
        Throws job reschedule exceptions if connection errors happen"""
        if config.unit_testing:
            raise Exception("Tried to run real http command in unit test")
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            return data
        except requests.ConnectionError as e:
            raise JobRescheduleConnectionError(10) from e
        except requests.ConnectTimeout as e:
            raise JobRescheduleConnectionTimeoutException(10) from e
        
    def ping_url(self, url: str):
        """Pings a url and returns response"""
        if config.unit_testing:
            raise Exception("Tried to run real http command in unit test")
        try:
            response = requests.get(url)
            return response
        except requests.ConnectionError as e:
            raise JobRescheduleConnectionError(10) from e
        except requests.ConnectTimeout as e:
            raise JobRescheduleConnectionTimeoutException(10) from e
        
    def get_file_stream(self, url):
        """Gets a file stream from a url"""
        if config.unit_testing:
            raise Exception("Tried to run real http command in unit test")
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            return response.raw
        except requests.ConnectionError as e:
            raise JobRescheduleConnectionError(10) from e
        except requests.ConnectTimeout as e:
            raise JobRescheduleConnectionTimeoutException(10) from e
