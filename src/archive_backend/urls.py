from django.http import HttpResponse
from django.urls import path, include
from rest_framework import routers

from archive_backend.jobs.syncing_jobs import download_remote_peer


from . import views

def testRoute(_):
    download_remote_peer("930c065f-e83c-4304-ac5a-3e4adfcd5741", "http://127.0.0.1:8000")
    return HttpResponse("No crashes")

urlpatterns = [
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path("", views.index, name="index"),
    path("", include('archive_backend.api.urls')),
    path("test", testRoute)
]