from django import forms 
  
# creating a form 
class TestForm(forms.Form): 
    title = forms.CharField() 
    description = forms.CharField()  
