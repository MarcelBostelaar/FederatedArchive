from django.http import HttpResponse
from django.urls import path, include
from rest_framework import routers



from . import views

def testRoute(_):
    # download_langauge("29cd547c-3b24-4945-9545-68f19231660c", "http://127.0.0.1:8000")
    return HttpResponse("No crashes")

urlpatterns = [
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path("", views.index, name="index"),
    path("", include('archive_backend.api')),
    path("test", testRoute)
]