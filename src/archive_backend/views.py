from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from .forms import TestForm

# Create your views here.

def index(request):
    return HttpResponse("<style>*{font-size:70px;}</style>Hello world.<br>\
                        <a href='admin'>Admin</a><br>\
                        <a href='api'>API</a><br>")
