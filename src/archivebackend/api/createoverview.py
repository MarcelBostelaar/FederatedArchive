import os
from django.core import serializers
from ArchiveSite.settings import BASE_DIR
from datetime import datetime

from archivebackend.models import *

def printer(classname, filename, filter):
    path = os.path.join(BASE_DIR, "static", filename + ".json")
    JSONSerializer = serializers.get_serializer("json")
    json_serializer = JSONSerializer()
    json_serializer.serialize(filter(classname.objects.all()), stream=open(path, "w"))

#TODO run periodically
def createAllOverviews():
    identityFilter = lambda x: x
    filterPeers = lambda x: x.filter(from_remote__isnull=True)
    printer(RemotePeer, "RemotePeers", identityFilter)
    for (prefix, filter) in [(identityFilter, "all"), (filterPeers, "local")]:
        printer(Author, prefix + "Authors", filter)
        printer(AuthorDescriptionTranslation, prefix + "AuthorDescriptionTranslations", filter)
        printer(AbstractDocument, prefix + "AbstractDocuments", filter)
        printer(AbstractDocumentDescriptionTranslation, prefix + "AbstractDocumentDescriptionTranslations", filter)
        printer(Edition, prefix + "Editions", filter)