from itertools import islice
from typing import Generator, Iterator, List


def flatten(x):
    return [item for sublist in x for item in sublist]

class registry:
    def __init__(self, registry_name_for_debugging = "unnamed"):
        self._registry = {}
        self._name = registry_name_for_debugging

    def register(self, key, value):
        if key in self._registry:
            raise ValueError(f"Duplicate registration of {key} in registry {self._name}")
        self._registry[key] = value

    def get(self, key):
        if key not in self._registry:
            raise ValueError(f"Item {key} is not registered in registry {self._name}")
        return self._registry[key]
    
    def override(self, key, value):
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
