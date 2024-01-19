import os
import tempfile
from django.core import serializers
from django.forms import model_to_dict
import requests
from ArchiveSite.settings import BASE_DIR
from datetime import datetime

from archivebackend.models import *

json_serializer = serializers.get_serializer("json")()

def printer(class_, filename, filter):
    path = os.path.join(BASE_DIR, "static", filename + ".json")
    json_serializer.serialize(filter(class_.objects.all()), stream=open(path, "w"))

#TODO run periodically
def createAllOverviews():
    identityFilter = lambda x: x
    filterPeers = lambda x: x.filter(from_remote__isnull=True)
    printer(RemotePeer, "RemotePeers", identityFilter)
    for (prefix, filter) in [(identityFilter, "all"), (filterPeers, "local")]:
        printer(Author, prefix + "Authors", filter)
        printer(Language, prefix + "Languages", filter)
        printer(AuthorDescriptionTranslation, prefix + "AuthorDescriptionTranslations", filter)
        printer(AbstractDocument, prefix + "AbstractDocuments", filter)
        printer(AbstractDocumentDescriptionTranslation, prefix + "AbstractDocumentDescriptionTranslations", filter)
        printer(Edition, prefix + "Editions", filter)


