def post_save_old_values(**signalkwargs):
    """Utility function to stop firing a post_save signal if the model instance does not meet the criteria.

    Will not fire on new instances. Relies on the FieldTracker utility from model_utils being called field_tracker in the model.

    The old values of the instance must be equal to the kwargs dictionary. (reference equality)"""
    def inner(func):
        def internal_filter(sender = None, instance = None, created = None, *args, **kwargs):
            if created:
                return #New items cant have old values
            if len(instance.field_tracker.changed()) == 0:
                return #No changes
            
            for key, value in signalkwargs.items():
                if not hasattr(instance, key):
                    raise Exception("Attribute " + key + " does not exist")
                oldValue = instance.field_tracker.previous(key)
                if value != oldValue:
                    return
            return func(sender, instance, created, *args, **kwargs)
        return internal_filter
    return inner

def post_save_new_values(**signalkwargs):
    """Utility function to stop firing a post_save signal if the model instance does not meet the criteria.

    The new values of the instance must be equal to the kwargs dictionary. (reference equality)"""
    def inner(func):
        def internal_filter(sender = None, instance = None, created = None, *args, **kwargs):
            for key, value in signalkwargs.items():
                if not hasattr(instance, key):
                    raise Exception("Attribute " + key + " does not exist")
                newValue = getattr(instance, key)
                if value != newValue:
                    return
            return func(sender, instance, created, *args, **kwargs)
        return internal_filter
    return inner

def post_save_new_values_NOTEQUALS_OR(**signalkwargs):
    """Utility function to stop firing a post_save signal if the model instance does not meet the criteria.

    None of the new values of the instance must be equal to the criteria in the kwargs dictionary, 
    meaning that if one equality matches, the signal wont fire. (reference equality)"""
    def inner(func):
        def internal_filter(sender = None, instance = None, created = None, *args, **kwargs):
            for key, value in signalkwargs.items():
                if not hasattr(instance, key):
                    raise Exception("Attribute " + key + " does not exist")
                newValue = getattr(instance, key)
                if value == newValue:
                    return
            return func(sender, instance, created, *args, **kwargs)
        return internal_filter
    return inner

def post_save_change_in_values(*valuesMustHaveChanged):
    """Utility function to stop firing a post_save signal if the model instance does not meet the criteria.

    Will not fire signal on new items.

    The values of the instance must have changed in the new data content. (reference equality)"""
    def inner(func):
        def internal_filter(sender = None, instance = None, created = None, *args, **kwargs):
            changes = instance.field_tracker.changed()
            if len(changes) == 0:
                return #No changes
            for key in valuesMustHaveChanged:
                if key not in changes.keys():
                    return #Key not changed
            return func(sender, instance, created, *args, **kwargs)
        return internal_filter
    return inner

def post_save_change_in_any(*valuesMustHaveChanged):
    """Utility function to stop firing a post_save signal if the model instance does not meet the criteria.

    Will not fire signal on new items.

    One of the given values of the instance must have changed in the new data content. (reference equality)"""
    def inner(func):
        def internal_filter(sender = None, instance = None, created = None, *args, **kwargs):
            changes = instance.field_tracker.changed()
            if len(changes) == 0:
                return #No changes
            for key in valuesMustHaveChanged:
                if key in changes.keys():
                    return func(sender, instance, created, *args, **kwargs)
            return
        return internal_filter
    return inner

def post_save_new_item():
    """Utility function to stop firing a post_save signal if the model instance does not meet the criteria.

    Will only fire signal on new items."""
    def inner(func):
        def internal_filter(sender = None, instance = None, created = None, *args, **kwargs):
            if created:
                return func(sender, instance, created, *args, **kwargs)
        return internal_filter
    return inner

def post_save_is_local_model(bool):
    """Only run the signal on local models, or only on remote models if set to False"""
    def inner(func):
        def internal_filter(sender = None, instance = None, created = None, *args, **kwargs):
            if instance.from_remote.is_this_site == bool:
                return func(sender, instance, created, *args, **kwargs)
        return internal_filter
    return inner