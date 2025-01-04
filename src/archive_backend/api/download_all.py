from archive_backend.jobs.job_decorator import jobify_model
from archive_backend.models import *
from archive_backend.api import *
from datetime import datetime

from archive_backend.signals.edition_signals import create_requestables
from archive_backend.signals.revision_signals import remote_revision_requestable_check
from archive_backend.utils.small import HttpUtil

update_order = [
        RemotePeer,
        Language,
        FileFormat,
        Author,
        AuthorDescriptionTranslation,
        AbstractDocument,
        AbstractDocumentDescriptionTranslation,
        Edition
] #Revision and ArchiveFile are not included because they are handled by signals based on server settings


@jobify_model("archive_backend.api.download_all.update_download_all", RemotePeer)
def update_download_all(from_remote: RemotePeer):
    """Updates all models that are from a remote peer.
    
    Does a full re-check and also a full download/update of all needed revisions and files if specified in the remotepeer config."""
    last_checkin = from_remote.last_checkin
    datetime_at_job_time = make_aware(datetime.now())

    for model in update_order:
        ViewContainer = ViewContainerRegistry.get(model)
        url = ViewContainer.get_list_url(on_site=from_remote.site_adress, updated_after=last_checkin)
        data = HttpUtil().get_json_from_remote(url)
        for item in data:
            #Use this method to
            # 1 Ensure possible table-self references are handled correctly (will send an additional request for each item), as well as catching any race conditions (item was updated in remote to reference new item made after sync of that table)
            # 2 Fire signals and save functions (which may contain validation logic and schedule other jobs)
            # While this may be slower than bulk create, jobs are not expected to be frequent and are handled by the background process
            SerializerRegistry.get(model).create_or_update_from_remote_data(item, from_remote.site_adress)
        if ViewContainer.is_alias_container():
            ViewContainer.download_aliases(from_remote.site_adress)

    for edition in Edition.objects.filter(from_remote=from_remote):
        create_requestables(edition)
    for revision in Revision.objects.filter(from_remote = from_remote, status=RevisionStatus.REQUESTABLE):
        remote_revision_requestable_check(revision)

    from_remote.last_checkin = datetime_at_job_time
    from_remote.save()