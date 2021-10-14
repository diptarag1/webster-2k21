from django import forms
from .models import Repo

class RepoCreateForm(forms.Form):
    rname = forms.CharField(max_length=30, required=True)

