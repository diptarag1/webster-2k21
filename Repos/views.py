from django.shortcuts import get_object_or_404, render, redirect,HttpResponse
from .forms import RepoCreateForm, AddCollaboratorForm
from .models import Repo
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.http import JsonResponse
import os
from .serverLocation import rw_dir

# Create your views here.
def init_Repo(request):
    if request.method == 'POST':
        form = RepoCreateForm(request.POST)
        if form.is_valid():
            new_repo = Repo(owner=request.user, repoURL=form.cleaned_data['rname'], name=form.cleaned_data['rname'])
            new_repo.repoURL = str(new_repo.owner) + '/' + new_repo.name
            new_repo.save()
            return redirect('home')  # for now
    else:
        form = RepoCreateForm()
    return render(request, 'Repos/repoCreate.html', {'form': form})


def detail_repo(request, name, owner, **kwargs):
    context = {}
    repo = Repo.objects.filter(name=name).filter(owner__username=owner).first()
    context['repo'] = repo
    if('subpath' in kwargs.keys()):
        allContents = os.listdir(os.path.join(rw_dir, owner, name, kwargs['subpath']))
    else:
        allContents = os.listdir(os.path.join(rw_dir, owner, name))
    contents = []
    for f in allContents:
        print(f)
        if not str(f).endswith('.git'):
            contents.append(f)
    context['contents'] = contents
    return render(request, 'Repos/repo_detail.html', context=context)


def delete_repo(request, name, owner):
    context = {}
    repo = Repo.objects.filter(name=name).filter(owner__username=owner).first()
    repo.delete()
    return redirect('home')


def add_remove_collaborator(request, ownerUsername, repoName):
    rName = str(ownerUsername) + '/' + repoName
    curRepo = get_object_or_404(Repo, repoURL=rName)
    if request.method == 'POST':
        form = AddCollaboratorForm(request.POST)
        if form.is_valid():
            collaborator = User.objects.filter(username=form.cleaned_data['collaboratorUsername']).first()
            if (curRepo.collaborators.filter(username=collaborator.username).exists()):
                curRepo.collaborators.remove(collaborator)
            else:
                curRepo.collaborators.add(collaborator)
            curRepo.save()
            return redirect('home')  # for now
    else:
        form = AddCollaboratorForm()
    return render(request, 'Repos/addCollaborator.html', {'form': form})


def star(request):
    id = request.POST.get('id')
    repo = Repo.objects.get(id=id)
    if request.user in repo.star.all():
        repo.star.remove(request.user)
    else:
        repo.star.add(request.user)
    context = {
        'repo': repo,
    }
    html = render_to_string('Repos/star-section.html', context, request=request)
    return JsonResponse({'html': html})

def fork(request,id):
    parent=Repo.objects.get(id=id)
    child=Repo.objects.filter(name=parent.name,owner=request.user)
    if(child.count()==0):
        new_repo=Repo.objects.create(parent=parent,owner=request.user,name=parent.name)
        new_repo.save()
    return redirect('home')
