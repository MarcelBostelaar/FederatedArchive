
import warnings
import requests
from archive_backend.models import *
from archive_backend.api import *
from datetime import datetime
from django_q.tasks import async_task

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

def get_json_from_remote(url: str):
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    return data

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

def download_revision(revision: Revision):
    """Downloads a revision from a remote"""
    warnings.warn("Executed download_revisions. This is not implemented yet")
    raise NotImplementedError("Not implemented yet")
    #TODO implement

def get_remote_revision_state(revision: Revision):
    raise NotImplementedError("Not implemented yet")
    #TODO implement

def schedule_task_until_success(func, *task_args, task_name=None, delayInMinutes = 5):
    """Schedules a task until it is successful"""
    def wrapped():
        try:
            func(*task_args)
        except Exception as e:
            pass
            # async_task(wrapped, task_name=task_name, delay=delayInMinutes*60)
    # async_task(wrapped, *task_args, task_name=task_name)
    raise NotImplementedError("Not implemented yet") #TODO

def trigger_remote_requestable(revision: Revision):
    """Requests a remote revision"""
    warnings.warn("Executed trigger_remote_requestable. This is not implemented yet")
    raise NotImplementedError("Not implemented yet")
    revision.status = RevisionStatus.REMOTEJOBSCHEDULED
    revision.save()