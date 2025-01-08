from django.http import HttpResponse
from django.urls import path, include
from rest_framework import routers

from archive_backend.models.archive_file import ArchiveFile
from archive_backend.models.remote_peer import RemotePeer
from archive_backend.models.revision import Revision, RevisionStatus



from . import views
import os
from django.http import FileResponse, Http404

def testRoute(_):
    # update_download_all(RemotePeer.objects.filter(site_name = "remote test").first())
    return HttpResponse("No crashes")

def basic_file_server(request, access, revision, filename):
    """Serves files from the archive_files directory, enforces basic access control based on revision status.
    
    Only admins can see files that are not published."""
    file_path = os.path.join('archive_files', access, str(revision), filename)
    if not os.path.exists(file_path):
        raise Http404("File not found")
    
    try:
        revision = Revision.objects.get(id=revision)
        if revision.status != RevisionStatus.ONDISKPUBLISHED:
            if not request.user.is_authenticated:
                return HttpResponse("Unauthorized", status=401)
            elif not request.user.is_staff:
                return HttpResponse("Forbidden", status=403)
        return FileResponse(open(file_path, 'rb'))
    except ArchiveFile.DoesNotExist:
        return Http404("File not found", status=404)

urlpatterns = [
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path("", views.index, name="index"),
    path("", include('archive_backend.api')),
    path("test", testRoute),
    path("archive_files/<str:access>/<uuid:revision>/<str:filename>", basic_file_server)
]