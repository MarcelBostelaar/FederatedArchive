from typing import List
from archive_backend.generation.structs import ProcessingFile
from archive_backend.models.edition import Edition

def fileProcessor(file : ProcessingFile):
    with file.getTextReadStream() as input:
        content = input.read()
    
    content = content.upper()
    
    finalFile = ProcessingFile(file.name + "_all_caps", file.format)
    with finalFile.getTextWriteStream() as outputfile:
        outputfile.write(content)
    
    return finalFile

def text_all_caps(origin_edition: Edition, target_edition: Edition, files: List[ProcessingFile],  config: dict) -> List[ProcessingFile]:
    """An example generator, takes a .txt file and outputs a new .txt files in all capital letters"""
    outputFiles = []
    for inputfile in files:
        if inputfile.format == "txt":
            outputFiles.append(fileProcessor(inputfile))
        else:
            outputFiles.append(inputfile)
    return outputFiles
