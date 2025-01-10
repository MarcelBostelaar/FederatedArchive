from django.http import HttpResponse
from django.urls import path, include

from .views import *


urlpatterns = [
    path('', index, name='home'),
    path('authors', authors, name='authors'),
]