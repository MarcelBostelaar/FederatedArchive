from django.dispatch import receiver
from django.core.signals import post_save

from archivebackend.models import Revision


#On version save, update url and last saved
@receiver(post_save)
def onRevisionSave(_model, modelInstance, isCreated, **_):
    if not _model == Revision:
        return
    #update edition url
    #update edition last saved
    #delete any old non-archived revisions
    raise NotImplementedError()

@receiver(post_save)
def onEditionChange(_model, modelInstance, isCreated, **_):
    #get all generated editions
    #mark them as ungenerated
    raise NotImplementedError()

@receiver(post_save)
def onEditionExistanceTypeChange(_model, modelInstance, isCreated, **_):
    #if it became ungenerated
        #if policy is to always generate, generate
    #if it became mirrored from remote, download files
    raise NotImplementedError()