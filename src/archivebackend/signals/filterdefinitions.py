from django.dispatch import receiver
from archivebackend.models import RemotePeer
from util import filterPreSave
from django.core.signals import post_save, pre_save


#RemotePeer signals
@receiver(pre_save, sender=RemotePeer)
@filterPreSave(RemotePeer, hasValues={"mirror_files" : True}, changeInValues=["mirror_files"])
def RemotePeerStartMirroring(_model, modelInstance, isCreated, *args, **kwargs):
    raise NotImplementedError()


@receiver(pre_save, sender=RemotePeer)
@filterPreSave(RemotePeer, hasValues={"mirror_files" : False}, changeInValues=["mirror_files"])
def RemotePeerStopMirroring(_model, modelInstance, isCreated, *args, **kwargs):
    raise NotImplementedError()

