from archive_backend.models.revision import RevisionStatus
from django.utils.text import get_valid_filename


def frontend_filepath_generator(instance):
    if instance.belongs_to.status == RevisionStatus.ONDISKPUBLISHED:
        status = "public/"
    else:
        status = "private/"
    return 'archive_files/' + status + str(instance.belongs_to.pk) + '/' + get_valid_filename(instance.file_name + "." + instance.file_format.format)