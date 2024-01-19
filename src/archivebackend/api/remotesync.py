import os
import tempfile
from django.forms import model_to_dict

import requests
from yaml import serialize_all
from ArchiveSite.settings import EDITIONS_URL

from archivebackend.models import *

def downloadFile(url, stream):
    chunk_size = 4096
    with requests.get(url, stream=True) as r:
        with stream as f:
            for chunk in r.iter_content(chunk_size): 
                if chunk:
                    f.write(chunk)

def reader(url):
    f = tempfile.TemporaryFile()
    downloadFile(url, f)
    return serialize_all.deserialize("json", f)

def updateOrInsertBatch(remotePeer, class_, batch):
    for deserialized_object in batch:
        defaults = {k: v for (k, v) in model_to_dict(deserialized_object).items()if k != 'id'}
        #if the remote peer is null, it is native to the peer, and not a peer of peer file, so it must be labled as such
        if(defaults["remote_peer"] is None):
            defaults["remote_peer"] = remotePeer
        class_.objects.update_or_create(
            id=deserialized_object.id,
            defaults=defaults
        )

def readRemote(remotePeer : RemotePeer):
    adress = remotePeer.site_adress
    localOnly = not remotePeer.peers_of_peer
    remote_id = remotePeer.pk
    
    prefix = "all"
    if localOnly:
        prefix = "local"
    updateOrInsertBatch(remote_id, RemotePeer, reader(adress + "/RemotePeers.json"))
    updateOrInsertBatch(remote_id, Author, reader(adress + "/" + prefix + "Authors.json"))
    updateOrInsertBatch(remote_id, Language, reader(adress + "/" + prefix + "Languages.json"))
    updateOrInsertBatch(remote_id, AuthorDescriptionTranslation, reader(adress + "/" + prefix + "AuthorDescriptionTranslations.json"))
    updateOrInsertBatch(remote_id, AbstractDocument, reader(adress + "/" + prefix + "AbstractDocuments.json"))
    updateOrInsertBatch(remote_id, AbstractDocumentDescriptionTranslation, reader(adress + "/" + prefix + "AbstractDocumentDescriptionTranslations.json"))
    editions = reader(adress + "/" + prefix + "Editions.json")
    for remoteEdition in editions:
        if remotePeer.mirror_files:
            remoteEdition.existance_type = existanceType.MIRROREDREMOTE
        else:
            remoteEdition.existance_type = existanceType.REMOTE
        
        if Edition.objects.filter(pk=remoteEdition.id).exists():
            if Edition.objects.filter(pk=remoteEdition.id).first().last_file_update < remoteEdition.last_file_update:
                updateFilesFromRemote(Edition.objects.filter(pk=remoteEdition.id).first())
    
    updateOrInsertBatch(remote_id, Edition, editions)

#TODO delay few seconds
def updateFilesFromRemote(instance: Edition):
    if(instance.existance_type == existanceType.MIRROREDREMOTE):
        #TODO
        print("Not implemented filesync, should sync an edition")
    pass