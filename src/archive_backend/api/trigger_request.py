

from django.http import HttpResponse
from archive_backend.models.revision import Revision, RevisionStatus


def trigger_revision_request(request, pk = None):
    if pk is None:
        return HttpResponse("No revision id provided", status=400)
    if not Revision.objects.filter(pk=pk).exists():
        return HttpResponse("Revision does not exist", status=404)
    revision = Revision.objects.get(pk=pk)
    match revision.status:
        case RevisionStatus.REMOTEREQUESTABLE:
            raise NotImplementedError() #TODO
        case RevisionStatus.REMOTEJOBSCHEDULED:
            raise NotImplementedError() #TODO
        case RevisionStatus.REQUESTABLE:
            raise NotImplementedError() #TODO
        case RevisionStatus.JOBSCHEDULED:
            HttpResponse("JOBSCHEDULED", status=200)
        case RevisionStatus.ONDISKPUBLISHED:
            HttpResponse("ONDISKPUBLISHED", status=200)
        case RevisionStatus.UNFINISHED:
            HttpResponse("Revision is not public", status=403)