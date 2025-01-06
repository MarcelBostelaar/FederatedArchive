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
    
def batched_bulk_create_boolresult(generator, cls, batch_size = None, ignore_conflicts = False) -> bool:
    """Bulk create a generator of objects in batches of batch_size.
    
    :param generator: A generator of the objects to create.
    :param cls: The class of the objects to create.
    :param batch_size: The size of the batches to create. If left as None, the generator will use the django default.
    :param ignore_conflicts: If True, the bulk_create will ignore conflicts.
    :return True if any objects were created, False otherwise."""
    items_before = cls.objects.count()
    while True:
        batch = list(islice(generator, batch_size))
        if not batch:
            break
        cls.objects.bulk_create(batch, batch_size, ignore_conflicts=ignore_conflicts)
    return items_before < cls.objects.count()

def batched_bulk_create(generator, cls, batch_size = None, ignore_conflicts = False) -> Iterator[any]:
    """Bulk create a generator of objects in batches of batch_size.
    
    Usefull for when you want to create lots of items in batches for performance but also use the results.
    
    :param generator: A generator of the objects to create.
    :param cls: The class of the objects to create.
    :param batch_size: The size of the batches to create. If left as None, the generator will use the django default.
    :param ignore_conflicts: If True, the bulk_create will ignore conflicts. WARNING, setting this to True will not return objects that caused conflicts as well, and will not set the pk's in some databases.
    :return A performant iterator for all created objects in order.
    """
    while True:
        batch = list(islice(generator, batch_size))
        if not batch:
            break
        made = cls.objects.bulk_create(batch, batch_size, ignore_conflicts=ignore_conflicts)
        for i in made:
            yield i

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
        
    def download_file(self, url):
        raise NotImplementedError("Not implemented")
