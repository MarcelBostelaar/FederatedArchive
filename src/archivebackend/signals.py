from django.dispatch import receiver
from django.core.signals import post_save

from archivebackend.models import Edition, Revision, existanceType

#Utility function
def filterPostSave(onlyClass, hasValues={}, changeInValues = []):
    def inner(func):
        def internal_filter(sender, modelInstance, *args, **kwargs):
            if not sender == onlyClass:
                return
            for (key, value) in hasValues:
                if not hasattr(modelInstance, key):
                    return
                if not getattr(modelInstance, key) == value:
                    return
            for key in changeInValues:
                if not hasattr(modelInstance, key):
                    return
            return func(sender, modelInstance, *args, **kwargs)
        return internal_filter
    return inner



@receiver(post_save)
@filterPostSave(Revision)
def updateEditionPrecalcsAndCleanRevision(_model, modelInstance, isCreated, *args, **kwargs):
    #update edition url
    #update edition last saved
    #delete any old non-archived revisions
    raise NotImplementedError()

@receiver(post_save)
@filterPostSave(Edition)
def propogateChangeInGenerationSource(_model, modelInstance, *args, **kwargs):
    for instance in modelInstance.generation_dependencies:
        instance.existance_type = existanceType.UNGENERATED

@receiver(post_save)
@filterPostSave(Edition, hasValues={"existance_type" : existanceType.UNGENERATED}, changeInValues=["existance_type"])
def onEditionBecameUngenerated(_model, modelInstance, isCreated, *args, **kwargs):
    #if policy is to always generate, generate
    raise NotImplementedError()

@receiver(post_save)
@filterPostSave(Edition, hasValues={"existance_type" : existanceType.MIRROREDREMOTE}, changeInValues=["existance_type"])
def onEditionBecameRemote(_model, modelInstance, isCreated, *args, **kwargs):
    #TODO download files
    raise NotImplementedError()