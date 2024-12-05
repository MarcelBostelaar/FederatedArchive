def not_new_items():
    """Utility function to stop firing a pre_save signal if the model instance is new"""
    def inner(func):
        def internal_filter(sender = None, instance = None, *args, **kwargs):
            if sender.objects.filter(pk=instance.pk).count() == 0:
                return
            return func(sender, instance, *args, **kwargs)
        return internal_filter
    return inner

def pre_save_new_values(**signalkwargs):
    """Utility function to stop firing a pre_save signal if the model instance does not meet the criteria.

    The values of the instance must meet the criteria in the kwargs dictionary"""
    def inner(func):
        def internal_filter(sender = None, instance = None, *args, **kwargs):
            for (key, value) in signalkwargs.items():
                if not hasattr(instance, key):
                    raise Exception("Attribute " + key + " does not exist")
                if not getattr(instance, key) == value:
                    return
            return func(sender, instance, *args, **kwargs)
        return internal_filter
    return inner

def pre_save_old_values(**signalkwargs):
    """Utility function to stop firing a pre_save signal if the model instance does not meet the criteria.

    If the model instance is new, the signal will not fire.

    The old values of the instance must meet the criteria in the kwargs dictionary"""
    def inner(func):
        def internal_filter(sender = None, instance = None, *args, **kwargs):
            if sender.objects.filter(pk=instance.pk).count() == 0:
                return
            old = sender.objects.get(pk = instance.pk)
            for key, value in signalkwargs.items():
                if not hasattr(instance, key):
                    raise Exception("Attribute " + key + " does not exist")
                oldValue = getattr(old, key)
                if value != oldValue:
                    return
            return func(sender, instance, *args, **kwargs)
        return internal_filter
    return inner

def pre_save_change_in_values(*valuesMustHaveChanged):
    """Utility function to stop firing a pre_save signal if the model instance does not meet the criteria.

    If the model instance is new, the signal will not fire.

    The values of the instance must have changed in the new data content"""
    def inner(func):
        def internal_filter(sender = None, instance = None, *args, **kwargs):
            if sender.objects.filter(pk=instance.pk).count() == 0:
                return
            old = sender.objects.get(pk = instance.pk)
            for key in valuesMustHaveChanged:
                if not hasattr(instance, key):
                    raise Exception("Attribute " + key + " does not exist")
                oldValue = getattr(old, key)
                if getattr(instance, key) == oldValue:
                    return
            return func(sender, instance, *args, **kwargs)
        return internal_filter
    return inner


## Post save

def post_save_old_values(**signalkwargs):
    """Utility function to stop firing a post_save signal if the model instance does not meet the criteria.

    If the model instance is new, the signal will not fire. Relies on the FieldTracker utility from model_utils being called field_tracker in the model.

    The old values of the instance must meet the criteria in the kwargs dictionary"""
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

    The new values of the instance must meet the criteria in the kwargs dictionary"""
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

def post_save_change_in_values(*valuesMustHaveChanged):
    """Utility function to stop firing a post_save signal if the model instance does not meet the criteria.

    Will not fire signal on new items.

    The values of the instance must have changed in the new data content"""
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

def post_save_new_item():
    """Utility function to stop firing a post_save signal if the model instance does not meet the criteria.

    Will not fire signal on new items.

    The values of the instance must have changed in the new data content"""
    def inner(func):
        def internal_filter(sender = None, instance = None, created = None, *args, **kwargs):
            if created:
                return func(sender, instance, created, *args, **kwargs)
        return internal_filter
    return inner