import shutil
from typing import List
from django.core.files import File

from archive_backend.models.file_format import FileFormat
from .structs import ProcessingFile
from .generator_registry import registered
from archive_backend.models.archive_file import ArchiveFile
from archive_backend.models.edition import Edition
from archive_backend.models.generation_config import GenerationConfig
from archive_backend.models.revision_file_models import Revision, RevisionStatus

def generatorLoop(ProcessingFiles: List[ProcessingFile], generatorConfig: GenerationConfig, originalEdition, targetEdition):
    generator = registered[generatorConfig.registered_name]
    if generator == None:
        raise ValueError("Generator not found in registry: ", generatorConfig.registered_name)
    newFiles = generator(originalEdition, targetEdition, ProcessingFiles, generatorConfig.config_json)

    if generatorConfig.next_step == None:
        return newFiles
    else:
        return generatorLoop(newFiles, generatorConfig.next_step, originalEdition, targetEdition)

def startGeneration(targetRevision: Revision):
    target_edition = targetRevision.belongs_to
    parent_edition = target_edition.actively_generated_from
    if parent_edition == None:
        raise ValueError("Parent edition of revision to generate is not of type generated")
    
    if targetRevision.status != RevisionStatus.JOBSCHEDULED:
        raise ValueError("Revision to generate must have a revision with status JOBSCHEDULED")

    most_recent_parent_revision = parent_edition.revisions.filter(status = RevisionStatus.ONDISKPUBLISHED).order_by('-date').first()
    if most_recent_parent_revision == None:
        raise ValueError("Parent edition of revision to generate has no published revision")


    #copying existing files to temporary files and wrapping them in ProcessingFiles
    startFiles = []

    for originalfile in most_recent_parent_revision.files.all():
        newProcessingFile = ProcessingFile(originalfile.file_name, originalfile.file_format.format)
        with originalfile.file.open('rb') as src, newProcessingFile.getWriteStream() as dst:
            shutil.copyfileobj(src, dst)
        startFiles.append(newProcessingFile)


    #Start the generation loop
    processed = generatorLoop(startFiles, target_edition.generation_config, parent_edition, target_edition)


    #Save the processed files to the database
    for processedFile in processed:
        with processedFile.getReadStream() as input:
            format = (FileFormat.objects.filter(format = processedFile.format).first()
            .allAliases().order_by('-from_remote__is_this_site').first())

            if format == None:
                raise ValueError("No matching file format found in database: ", processedFile.format)

            newFile = File(input)

            archiveFile = ArchiveFile.objects.create(
                belongs_to = targetRevision,
                file_format = format
            )
            archiveFile.saveFile(newFile).save()

    targetRevision.status = RevisionStatus.ONDISKPUBLISHED
    targetRevision.date = target_edition.date.now()
    targetRevision.save()