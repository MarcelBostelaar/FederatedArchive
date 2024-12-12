from django.urls import path, include
from rest_framework import routers


from . import views

urlpatterns = [
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path("", views.index, name="index"),
    path("", include('archive_backend.api.urls')),
]