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

# def pre_save_value_filter(newValuesMustContain={}, valuesMustHaveChanged = [], oldValuesMustBe={}):
#     """Utility function to stop firing a signal if the model instance does not meet the criteria.
#     hasValues is a dictionary of the values that must be set in the new data content of the model.
#     changeinAnyValues is a list of values that must be changed in the new data content of the model.
#     Prevents firing of signal on object creation"""
#     def inner(func):
#         def internal_filter(sender = None, instance = None, *args, **kwargs):
#             for (key, value) in newValuesMustContain.items():
#                 if not hasattr(instance, key):
#                     raise Exception("Attribute " + key + " does not exist")
#                 if not getattr(instance, key) == value:
#                     return
                
#             if sender.objects.filter(pk=instance.pk).count() == 0:
#                 if len(oldValuesMustBe.items()) > 0:
#                     return #new instance cant have old values
#                 return func(sender, instance, *args, **kwargs)#new item, values have always changed, fire
                
#             old = sender.objects.get(pk = instance.pk)
#             for key in valuesMustHaveChanged:
#                 if not hasattr(instance, key):
#                     raise Exception("Attribute " + key + " does not exist")
#                 oldValue = getattr(old, key)
#                 if getattr(instance, key) == oldValue:
#                     return #Value did not change, so dont fire
                
#             for key, value in oldValuesMustBe.items():
#                 if not hasattr(instance, key):
#                     raise Exception("Attribute " + key + " does not exist")
#                 oldValue = getattr(old, key)
#                 if value != oldValue:
#                     return #Value wasnt right in the previous state, so dont fire
                
#             return func(sender, instance, *args, **kwargs)#All checks passed, fire
#         return internal_filter
#     return inner





# @receiver(post_save, sender = Revision)
# def updateEditionPrecalcsAndCleanRevision(_model, modelInstance, isCreated, *args, **kwargs):
#     #update edition url
#     #update edition last saved
#     #delete any old non-archived revisions
#     raise NotImplementedError()

# @receiver(post_save, Sender = Edition)
# def propogateChangeInGenerationSource(_model, modelInstance, *args, **kwargs):
#     for instance in modelInstance.generation_dependencies:
#         instance.existance_type = existanceType.UNGENERATED

# @receiver(pre_save, sender=Edition)
# @filterPreSave(Edition, hasValues={"existance_type" : existanceType.UNGENERATED}, changeInValues=["existance_type"])
# def onEditionBecameUngenerated(_model, modelInstance, isCreated, *args, **kwargs):
#     #if policy is to always generate, generate
#     raise NotImplementedError()

# @receiver(pre_save, sender=Edition)
# @filterPreSave(Edition, hasValues={"existance_type" : existanceType.MIRROREDREMOTE}, changeInValues=["existance_type"])
# def onEditionBecameRemote(_model, modelInstance, isCreated, *args, **kwargs):
#     #TODO download files
#     raise NotImplementedError()