from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from archivebackend.api.createoverview import createAllOverviews

from archivebackend.forms import TestForm

# Create your views here.

def index(request):
    return HttpResponse("Hello, world. You're at the index.")

def test_view(request): 
    # if this is a POST request we need to process the form data
    if request.method == "POST":
        # create a form instance and populate it with data from the request:
        form = TestForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            createAllOverviews()
            return HttpResponseRedirect("/thanks/")
    context ={} 
    context['form']= TestForm() 
    return render(request, "test.html", context) 