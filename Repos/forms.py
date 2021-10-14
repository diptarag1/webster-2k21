from django import forms
from .models import Repo

class RepoCreateForm(forms.Form):
    rname = forms.CharField(max_length=30, required=True)

class AddCollaboratorForm(forms.Form):
    collaboratorUsername = forms.CharField(max_length=100, required=True)