from django.http import HttpResponse

from archive_backend.generation.generation_handler import startGeneration
from archive_backend.jobs.job_exceptions import BaseJobRescheduleException
from .serializers import ArchiveFileSerializer, RevisionSerializer
from archive_backend.models.revision import Revision, RevisionStatus
from archive_backend.utils.small import HttpUtil
from .apiviews import api_subpath, ArchiveFileViews, RevisionViews

trigger_request_base = api_subpath + "/revision/trigger/"
def getTriggerRequestUrl(revision: Revision):
    return trigger_request_base + str(revision.id)

def trigger_requestable(revision: Revision):
    match revision.status:
        case RevisionStatus.UNFINISHED:
            raise Exception("Cannot trigger requestable for an unfinished revision")
        case RevisionStatus.ONDISKPUBLISHED:
            return
        case RevisionStatus.JOBSCHEDULED:
            return
        case RevisionStatus.REMOTEJOBSCHEDULED:
            trigger_remote_requestable(revision)
            return
        case RevisionStatus.REMOTEREQUESTABLE:
            trigger_remote_requestable(revision)
            return
        case RevisionStatus.REQUESTABLE:
            match [revision.generated_from, revision.from_remote.is_this_site]:
                case [None, True]:
                    raise Exception("Local requestable revision has no generation source")
                case [None, False]:
                    full_download_remote_revision(revision)
                    return
                case [_, True]:
                    startGeneration(revision)
                    return
                case [_, False]:
                    raise Exception("Remote requestable revision has a generation source")

#TODO jobify
def trigger_remote_requestable(revision: Revision):
    response = HttpUtil().ping_url(getTriggerRequestUrl(revision))
    if response.code >= 500:
        raise BaseJobRescheduleException(10, f"Remote server returned {response.code} error.")
    if response.code >= 400:
        raise Exception(f"Remote server returned {response.code} error")
    if response.code >= 300:
        raise Exception(10, f"Remote server returned {response.code} error")
    #update own data from remote to have status be as up to date as possible
    RevisionSerializer.download_or_update_from_remote_site(revision.id, revision.from_remote.site_adress)

#TODO jobify
def full_download_remote_revision(revision: Revision):
    if revision.status != RevisionStatus.REQUESTABLE or revision.status != RevisionStatus.JOBSCHEDULED:
        raise Exception("Cannot download a remote revision that is not requestable or scheduled for download")
    if revision.from_remote.is_this_site:
        raise Exception("Cannot download a local revision")
    remote_status = get_remote_revision_state(revision)
    
    revision.status = RevisionStatus.JOBSCHEDULED
    revision.save()

    match remote_status:
        case RevisionStatus.REQUESTABLE:
            trigger_remote_requestable(revision)
            raise BaseJobRescheduleException(10, "Remote revision is not published yet, but request to do so is now send")
        case RevisionStatus.REMOTEREQUESTABLE:
            trigger_remote_requestable(revision)
            raise BaseJobRescheduleException(10, "Remote revision is not published yet, but request to do so is now send")
        case RevisionStatus.JOBSCHEDULED:
            raise BaseJobRescheduleException(10, "Remote revision is not published yet, but it is scheduled")
        case RevisionStatus.REMOTEJOBSCHEDULED:
            raise BaseJobRescheduleException(10, "Remote revision is not published yet, but it is scheduled")
        case RevisionStatus.ONDISKPUBLISHED:
            url = ArchiveFileViews.get_list_url(related_revision=revision.id, on_site=revision.from_remote.site_adress)
            data = HttpUtil().get_json_from_remote(url)
            for item in data:
                ArchiveFileSerializer.create_or_update_from_remote_data(item, revision.from_remote.site_adress)
        case _:
            raise Exception(f"Invalid remote status {remote_status}")
        

def get_remote_revision_state(revision: Revision):
    data = HttpUtil().get_json_from_remote(RevisionViews.get_detail_url(revision.id, on_site=revision.from_remote.site_adress))
    if data is {}:
        raise Exception("No remote revision found for this id: " + str(revision.id))
    status = RevisionStatus(data["status"])
    return status

def trigger_revision_request_endpoint(request, pk = None):
    if pk is None:
        return HttpResponse("No revision id provided", status=400)
    if not Revision.objects.filter(pk=pk).exists():
        return HttpResponse("Revision does not exist", status=404)
    revision = Revision.objects.get(pk=pk)
    match revision.status:
        case RevisionStatus.UNFINISHED:
            return HttpResponse("Revision is not public", status=403)
        case RevisionStatus.REMOTEREQUESTABLE:
            trigger_requestable(revision)
        case RevisionStatus.REMOTEJOBSCHEDULED:
            trigger_requestable(revision)
        case RevisionStatus.REQUESTABLE:
            trigger_requestable(revision)
        case RevisionStatus.JOBSCHEDULED:
            pass
        case RevisionStatus.ONDISKPUBLISHED:
            pass
    return HttpResponse(revision.status, status=200)