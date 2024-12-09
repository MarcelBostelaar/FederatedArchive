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