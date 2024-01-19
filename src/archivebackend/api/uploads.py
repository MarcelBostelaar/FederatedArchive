import os
from archivebackend.models import Edition

def uploadSeveralDocuments(saveTo, deleteOld, *files):
    """Writes documents to a specified folder and returns the entry point to acces said files.
    Relative url to the file if only one exists
    Relative url to the folder if multiple or none exist"""
    if(deleteOld):
        os.rmdir(saveTo)
        os.mkdir(saveTo)
    os.makedirs(saveTo, exist_ok=True)
    for file in files:
        writeObjectBinary(os.path.join(saveTo, file.name), file)
    files = os.listdir(saveTo)
    url = saveTo
    if(len(files) == 1):
        url = os.path.join(url, files[0])
    return url

        
def writeObjectBinary(filepath, inMemoryFile):
    with open(filepath, "wb") as file:
        for chunk in inMemoryFile.chunks():
            file.write(chunk)