

def pre_save_not_new_items():
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

    The new values of the instance be equal to the kwargs dictionary. (reference equality)"""
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

    Will not fire on new instances.

    The old values of the instance be equal to the kwargs dictionary. (reference equality)"""
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

    Will not fire on new instances.

    The values of the instance must have changed in the new data content. (reference equality)"""
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

