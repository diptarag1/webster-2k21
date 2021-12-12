from django.shortcuts import get_object_or_404, render, redirect,HttpResponse
from .forms import RepoCreateForm, AddCollaboratorForm,IssueCreateForm
from .models import Repo,Issue
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
    return render(request, 'Repos/repoCreate.html', {'form': form,'randomUniqueName':"newDivaniRepo"})


def detail_repo(request, name, owner, **kwargs):
    context = {}
    repo = Repo.objects.filter(name=name).filter(owner__username=owner).first()
    context['repo'] = repo

    context['name'] = name
    context['owner'] = owner
    
    curDir = os.path.join(rw_dir, owner, name)
    teDir=''
    if('subpath' in kwargs.keys()):
        curDir = os.path.join(curDir, kwargs['subpath'])
        teDir=teDir+kwargs['subpath']
        context['subpath'] = kwargs['subpath']

    allContents = os.listdir(curDir)
    fileContents = []
    dirContents = []

    for f in allContents:
        if not str(f).endswith('.git'):
            if(os.path.isfile(os.path.join(curDir, str(f)))):
                fileContents.append(f)
            else:
                dirContents.append(f)

    context['fileContents'] = fileContents
    context['dirContents'] = dirContents
    context['curDir'] = teDir
    context['forkedChild']=Repo.objects.filter(parent=repo)
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
    parent = Repo.objects.get(id=id)
    new_repo=Repo.objects.create(parent=parent,owner=request.user,name=parent.name,is_private=False)
    new_repo.create_fork(parent)
    new_repo.save()

    return redirect('home')


def create_issue(request,owner,name):
    context={}
    if request.method=='GET':
        context['form']=IssueCreateForm()
    else:
        form=IssueCreateForm(request.POST)
        form.instance.author=request.user
        form.instance.repo=Repo.objects.get(owner__username=owner,name=name)
        form.save()
        return redirect('detail_repo',owner=owner,name=name)
    return render(request,'Repos/issue_create_form.html',context=context)

def issue_list(request,owner,name):
    context={}
    repo=Repo.objects.get(owner__username=owner,name=name)
    issues=Issue.objects.filter(repo=repo)
    context['issues']=issues
    return render(request,'Repos/issues_list.html',context=context)
