from archive_backend.models import *
from archive_backend.api import *
from datetime import datetime

from archive_backend.utils.small import get_json_from_remote

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


#TODO jobify
def update_download_all(from_remote: RemotePeer):
    last_checkin = from_remote.last_checkin
    datetime_at_job_time = datetime.now()

    for model in update_order:
        ViewContainer = ViewContainerRegistry.get(model)
        url = ViewContainer.get_list_url(on_site=from_remote.site_adress, updated_after=last_checkin)
        data = get_json_from_remote(url)
        for item in data:
            #Use this method to
            # 1 Ensure possible table-self references are handled correctly (will send an additional request for each item), as well as catching any race conditions (item was updated in remote to reference new item made after sync of that table)
            # 2 Fire signals and save functions (which may contain validation logic and schedule other jobs)
            # While this may be slower than bulk create, jobs are not expected to be frequent and are handled by the background process
            SerializerRegistry.get(model).create_or_update_from_remote_data(item, from_remote.site_adress)
        if ViewContainer.is_alias_container():
            ViewContainer.download_aliases(from_remote.site_adress)

    from_remote.last_checkin = datetime_at_job_time
    from_remote.save()