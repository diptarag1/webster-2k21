from django.shortcuts import get_object_or_404, render, redirect
from .forms import RepoCreateForm, AddCollaboratorForm
from .models import Repo
from django.contrib.auth.models import User

# Create your views here.
def init_Repo(request):
    if request.method == 'POST':
        form = RepoCreateForm(request.POST)
        if form.is_valid():
            new_repo = Repo(owner = request.user, repoURL = form.cleaned_data['rname'])
            new_repo.repoURL = str(new_repo.owner) + '/' + new_repo.repoURL
            new_repo.save()
            return redirect('home') #for now
    else:
        form = RepoCreateForm()
    return render(request, 'Repos/repoCreate.html', {'form': form})


def add_remove_collaborator(request, ownerUsername, repoName):
    rName = str(ownerUsername) + '/' + repoName
    curRepo = get_object_or_404(Repo, repoURL = rName)
    if request.method == 'POST':
        form = AddCollaboratorForm(request.POST)
        if form.is_valid():
            collaborator = User.objects.filter(username = form.cleaned_data['collaboratorUsername']).first()
            if(curRepo.collaborators.filter(username = collaborator.username).exists()):
                curRepo.collaborators.remove(collaborator)
            else:
                curRepo.collaborators.add(collaborator)
            curRepo.save()
            return redirect('home') #for now
    else:
        form = AddCollaboratorForm()
    return render(request, 'Repos/addCollaborator.html', {'form': form})