from django import forms
from .models import Repo,Issue

class RepoCreateForm(forms.Form):
    rname = forms.CharField(max_length=30, required=True)

class AddCollaboratorForm(forms.Form):
    collaboratorUsername = forms.CharField(max_length=100, required=True)

class IssueCreateForm(forms.ModelForm):
    class Meta:
        model=Issue
        fields=['topic','description','tags']