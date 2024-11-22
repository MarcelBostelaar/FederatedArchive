import datetime
from django.dispatch import receiver
from django.core.signals import post_save, pre_save
from archivebackend.models import Edition, Revision, existanceType

def filterPreSave(hasValues={}, changeInAnyValues = []):
    """Utility function to stop firing a signal if the model instance does not meet the criteria.
    hasValues is a dictionary of the values that must be set in the new data content of the model.
    changeinAnyValues is a list of values that must be changed in the new data content of the model"""
    def inner(func):
        def internal_filter(sender, modelInstance, *args, **kwargs):
            for (key, value) in hasValues:
                if not hasattr(modelInstance, key):
                    raise Exception("Attribute " + key + " does not exist")
                if not getattr(modelInstance, key) == value:
                    return
            if modelInstance.pk is None or len(changeInAnyValues) == 0:
                #New instance or no changes in values need to be detected
                return func(sender, modelInstance, *args, **kwargs)
            else:
                old = sender.get(pk = modelInstance.pk)
                for key in changeInAnyValues:
                    if not hasattr(modelInstance, key):
                        raise Exception("Attribute " + key + " does not exist")
                    if getattr(modelInstance, key) != getattr(old, key):
                        return func(sender, modelInstance, *args, **kwargs)
                return #No changes in values, dont fire
        return internal_filter
    return inner





@receiver(post_save, sender = Revision)
def updateEditionPrecalcsAndCleanRevision(_model, modelInstance, isCreated, *args, **kwargs):
    #update edition url
    #update edition last saved
    #delete any old non-archived revisions
    raise NotImplementedError()

@receiver(post_save, Sender = Edition)
def propogateChangeInGenerationSource(_model, modelInstance, *args, **kwargs):
    for instance in modelInstance.generation_dependencies:
        instance.existance_type = existanceType.UNGENERATED

@receiver(pre_save, sender=Edition)
@filterPreSave(Edition, hasValues={"existance_type" : existanceType.UNGENERATED}, changeInValues=["existance_type"])
def onEditionBecameUngenerated(_model, modelInstance, isCreated, *args, **kwargs):
    #if policy is to always generate, generate
    raise NotImplementedError()

@receiver(pre_save, sender=Edition)
@filterPreSave(Edition, hasValues={"existance_type" : existanceType.MIRROREDREMOTE}, changeInValues=["existance_type"])
def onEditionBecameRemote(_model, modelInstance, isCreated, *args, **kwargs):
    #TODO download files
    raise NotImplementedError()