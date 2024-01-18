import os
from django.core import serializers
from ArchiveSite.settings import BASE_DIR
from datetime import datetime

from archivebackend.models import *

class serializeUtil():
    """Makes serializing many django objects into one json a bit neater"""
    def __init__(self, out) -> None:
        self.out = out
        JSONSerializer = serializers.get_serializer("json")
        self.json_serializer = JSONSerializer()
        
    def p(self, someString):
        """Prints a string"""
        self.out.write(someString)
        return self
    
    def s(self, someDjangoObject):
        """Serializes a django object"""
        self.json_serializer.serialize(someDjangoObject, stream=self.out)
        return self
    
    def close(self):
        self.out.close()

def printer(onlyLocal, classname, filename):
    filterPeers = lambda x: x
    prefix = "all"
    if onlyLocal:
        filterPeers = lambda x: x.filter(from_remote__isnull=True)
        prefix = "local"
    path = os.path.join(BASE_DIR, "static", prefix + filename + ".json")
    JSONSerializer = serializers.get_serializer("json")
    json_serializer = JSONSerializer()
    json_serializer.serialize(filterPeers(classname.objects.all()), stream=open(path, "w"))

#TODO run periodically
def createAllOverviews():
    for i in [True, False]:
        printer(i, Author, "Authors")
        # printer(i, RemotePeer, "RemotePeers") #TODO seperate
        printer(i, AuthorDescriptionTranslation, "AuthorDescriptionTranslations")
        printer(i, AbstractDocument, "AbstractDocuments")
        printer(i, AbstractDocumentDescriptionTranslation, "AbstractDocumentDescriptionTranslations")
        printer(i, Edition, "Editions")

    # lambda printer (prefix_, filter_, class_, filename): 

    # json_serializer(filterPeers(Author.objects.all()), stream=open())

    # serializeUtil(streamOut)\
    # .p("{")\
    #     .p('"Authors":').s(filterPeers(Author.objects.all())).p(",")\
    #     .p('"RemotePeers":').s(RemotePeers.objects.all()).p(",")\
    #     .p('"AuthorDescriptionTranslations":').s(filterPeers(AuthorDescriptionTranslation.objects.all())).p(",")\
    #     .p('"AbstractDocuments":').s(filterPeers(AbstractDocument.objects.all())).p(",")\
    #     .p('"AbstractDocumentDescriptionTranslations":').s(filterPeers(AbstractDocumentDescriptionTranslation.objects.all())).p(",")\
    #     .p('"Editions":').s(filterPeers(Edition.objects.all()))\
    # .p("}")\
    # .close()

# #TODO run periodically
# def createAllOverviews():
#     createOverview(False, open(os.path.join(BASE_DIR, "static", "localdata.json"), "w"))
#     createOverview(True, open(os.path.join(BASE_DIR, "static", "alldata.json"), "w"))
    