from django.http import HttpResponse
from django.urls import path, include
from rest_framework import routers

from archive_backend.models.remote_peer import RemotePeer



from . import views

def testRoute(_):
    # update_download_all(RemotePeer.objects.filter(site_name = "remote test").first())
    return HttpResponse("No crashes")

urlpatterns = [
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path("", views.index, name="index"),
    path("", include('archive_backend.api')),
    path("test", testRoute)
]