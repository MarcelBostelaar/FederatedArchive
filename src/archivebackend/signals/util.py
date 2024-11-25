def not_new_items():
    """Utility function to stop firing a pre_save signal if the model instance is new"""
    def inner(func):
        def internal_filter(sender = None, instance = None, *args, **kwargs):
            if sender.objects.filter(pk=instance.pk).count() == 0:
                return
            return func(sender, instance, *args, **kwargs)
        return internal_filter
    return inner

def pre_save_value_filter(newValuesMustContain={}, valuesMustHaveChanged = []):
    """Utility function to stop firing a signal if the model instance does not meet the criteria.
    hasValues is a dictionary of the values that must be set in the new data content of the model.
    changeinAnyValues is a list of values that must be changed in the new data content of the model.
    Prevents firing of signal on object creation"""
    def inner(func):
        def internal_filter(sender = None, instance = None, *args, **kwargs):
            for (key, value) in newValuesMustContain.items():
                if not hasattr(instance, key):
                    raise Exception("Attribute " + key + " does not exist")
                if not getattr(instance, key) == value:
                    return
            if sender.objects.filter(pk=instance.pk).count() == 0 or len(valuesMustHaveChanged) == 0:
                #New instance or no changes in values need to be detected
                return func(sender, instance, *args, **kwargs)
            else:
                old = sender.objects.get(pk = instance.pk)
                for key in valuesMustHaveChanged:
                    if not hasattr(instance, key):
                        raise Exception("Attribute " + key + " does not exist")
                    attribute = getattr(old, key)
                    if getattr(instance, key) != attribute:
                        return func(sender, instance, *args, **kwargs)
                return #No changes in values, dont fire
        return internal_filter
    return inner





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