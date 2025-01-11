from django.http import HttpResponse
from django.shortcuts import render
from django.core.serializers import serialize

from archive_backend.models import *

# Create your views here.

def index(request):
    context = {}
    context["authorcount"] = Author.objects.values('alias_identifier').distinct().count()
    context["documentcount"] = AbstractDocument.objects.values('alias_identifier').distinct().count()
    return render(request, "index.html", context)

def authors(request):
    context = {}
    test = list(Author.objects.all())
    context["authors"] = Author.objects.all()#.prefetch_related("descriptions__language"))
    return render(request, "authors.html", context)