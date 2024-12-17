

from django.http import HttpResponse
from archive_backend.models.revision import Revision, RevisionStatus
from archive_backend.signals.revision_signals import trigger_remote_requestable, trigger_requestable


def trigger_revision_request(request, pk = None):
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