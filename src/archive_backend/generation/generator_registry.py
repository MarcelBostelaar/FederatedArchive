registered = {}

def register_generator(name, callback):
    """Register a generator function. Ensure your name is unique among all generators."""
    if name in registered:
        raise ValueError("Generator name already exists")
    registered[name] = callback

