import os
from archivebackend.models import Edition

def uploadSeveralDocuments(saveTo, deleteOld, *files):
    """Writes documents to a specified folder and returns the entry point to acces said files
    Name of single existing file if one file exists in folder
    Empty string if multiple (or no) files exist"""
    if(deleteOld):
        os.rmdir(saveTo)
        os.mkdir(saveTo)
    os.makedirs(saveTo, exist_ok=True)
    for file in files:
        writeObjectBinary(os.path.join(saveTo, file.name), file)
    files = os.listdir(saveTo)
    root_file = ""
    if(len(files) == 1):
        root_file = files[0]
    return root_file

        
def writeObjectBinary(filepath, inMemoryFile):
    with open(filepath, "wb") as file:
        for chunk in inMemoryFile.chunks():
            file.write(chunk)