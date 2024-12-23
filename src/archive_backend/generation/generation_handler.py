from datetime import datetime
import shutil
from typing import List
from django.core.files import File

from archive_backend.jobs.job_decorator import jobify_model
from archive_backend.models.file_format import FileFormat
from .structs import ProcessingFile
from .generation_registries import generators
from archive_backend.models.archive_file import ArchiveFile
from archive_backend.models.edition import Edition
from archive_backend.models.generation_config import GenerationConfig
from archive_backend.models.revision import Revision, RevisionStatus

def generatorLoop(ProcessingFiles: List[ProcessingFile], generatorConfig: GenerationConfig, originalEdition, targetEdition):
    generator = generators.get(generatorConfig.registered_name)
    newFiles = generator(originalEdition, targetEdition, ProcessingFiles, generatorConfig.config_json)

    if generatorConfig.next_step == None:
        return newFiles
    else:
        return generatorLoop(newFiles, generatorConfig.next_step, originalEdition, targetEdition)

@jobify_model("archive_backend.generation.generation_handler.startGeneration", Revision)
def startGeneration(to_generate: Revision):
    if to_generate.generated_from == None:
        raise ValueError("Revision to generate must have a revision it is generated from")
    if to_generate.status == RevisionStatus.ONDISKPUBLISHED:
        return #Already done
    if to_generate.status != RevisionStatus.JOBSCHEDULED:
        raise ValueError("Revision to generate must have a revision with status JOBSCHEDULED")
    if not to_generate.from_remote.is_this_site:
        raise ValueError("Revision to generate must be from this site")
    own_edition = to_generate.belongs_to
    source_edition = to_generate.generated_from.belongs_to
    source_revision = to_generate.generated_from

    #copying existing files to temporary files and wrapping them in ProcessingFiles
    startFiles = []

    for originalfile in source_revision.files.all():
        newProcessingFile = ProcessingFile(originalfile.file_name, originalfile.file_format.format)
        with originalfile.file.open('rb') as src, newProcessingFile.getWriteStream() as dst:
            shutil.copyfileobj(src, dst)
        startFiles.append(newProcessingFile)


    #Start the generation loop
    processed = generatorLoop(startFiles, own_edition.generation_config, source_edition, own_edition)

    #Save the processed files to the database
    for processedFile in processed:
        with processedFile.getReadStream() as input:
            format = (FileFormat.objects.filter(format = processedFile.format).first()
            .allAliases().order_by('-from_remote__is_this_site').first())

            if format == None:
                raise ValueError("No matching file format found in database: ", processedFile.format)

            newFile = File(input)

            archiveFile = ArchiveFile.objects.create(
                belongs_to = to_generate,
                file_format = format,
                file_name = processedFile.name
            )
            archiveFile.saveFile(newFile).save()

    to_generate.status = RevisionStatus.ONDISKPUBLISHED
    to_generate.date = datetime.now()
    to_generate.save()