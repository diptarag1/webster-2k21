from django import forms
from .models import PullRequest, Repo,Issue,IssueComment

class RepoCreateForm(forms.Form):
    rname = forms.CharField(max_length=30, required=True)

class AddCollaboratorForm(forms.Form):
    collaboratorUsername = forms.CharField(max_length=100, required=True)

class IssueCreateForm(forms.ModelForm):
    class Meta:
        model=Issue
        fields=['topic','description','tags']

class IssueCommentCreateForm(forms.ModelForm):
    class Meta:
        model=IssueComment
        fields=['data']


class PullRequestCreateForm(forms.ModelForm):
    class Meta:
        model=PullRequest
        fields=['base_branch', 'feature_branch', 'parentBit']