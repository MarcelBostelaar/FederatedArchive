from itertools import islice
from typing import Generator, Iterator, List


def flatten(x):
    return [item for sublist in x for item in sublist]

class registry:
    def __init__(self):
        self._registry = {}

    def register(self, name, value):
        if name in self._registry:
            raise ValueError(f"Duplicate registration of {name}")
        self._registry[name] = value

    def get(self, name):
        if name not in self._registry:
            raise ValueError(f"Item {name} is not registered")
        return self._registry[name]
    
def batched_bulk_create_boolresult(generator, cls, batch_size = None, ignore_conflicts = False) -> bool:
    """Bulk create a generator of objects in batches of batch_size.
    
    :param generator: A generator of the objects to create.
    :param cls: The class of the objects to create.
    :param batch_size: The size of the batches to create. If left as None, the generator will use the django default.
    :param ignore_conflicts: If True, the bulk_create will ignore conflicts.
    :return True if any objects were created, False otherwise."""
    made_any = False
    while True:
        batch = list(islice(generator, batch_size))
        if not batch:
            break
        made = cls.objects.bulk_create(batch, batch_size, ignore_conflicts=ignore_conflicts)
        if len(made) > 0:
            made_any = True
    return made_any

def batched_bulk_create(generator, cls, batch_size = None, ignore_conflicts = False) -> Iterator[any]:
    """Bulk create a generator of objects in batches of batch_size.
    
    Usefull for when you want to create lots of items in batches for performance but also use the results.
    
    :param generator: A generator of the objects to create.
    :param cls: The class of the objects to create.
    :param batch_size: The size of the batches to create. If left as None, the generator will use the django default.
    :param ignore_conflicts: If True, the bulk_create will ignore conflicts.
    :return A performant iterator for all created objects in order.
    """
    while True:
        batch = list(islice(generator, batch_size))
        if not batch:
            break
        made = cls.objects.bulk_create(batch, batch_size, ignore_conflicts=ignore_conflicts)
        if len(made) > 0:
            for i in made:
                yield i
