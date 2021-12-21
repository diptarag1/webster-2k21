from django.shortcuts import get_object_or_404, render, redirect,HttpResponse
from .forms import RepoCreateForm, AddCollaboratorForm,IssueCreateForm
from .models import Repo, Issue
from user.models import Activity
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.http import JsonResponse
import os
from .serverLocation import rw_dir
from git import Git,Repo as _Repo
import git
import subprocess
# Create your views here.
def init_Repo(request):
    if request.method == 'POST':
        form = RepoCreateForm(request.POST)
        if form.is_valid():
            new_repo = Repo(owner=request.user, repoURL=form.cleaned_data['rname'], name=form.cleaned_data['rname'])
            new_repo.repoURL = str(new_repo.owner) + '/' + new_repo.name
            new_repo.save()
            new_repo.collaborators.add(request.user)
            new_repo.save()
            subprocess.call(['chmod','-R','777',rw_dir+new_repo.repoURL+".git"])
            git.Git(rw_dir+request.user.username).clone(rw_dir+new_repo.repoURL+".git")
            activity=Activity.createdRepo(request.user,new_repo)
            activity.save()
            print(activity)
            return redirect('home')  # for now
    else:
        form = RepoCreateForm()
    return render(request, 'Repos/repoCreate.html', {'form': form,'randomUniqueName':"newDivaniRepo"})



def prepare_context(name, owner, branch, repo):

    context = { }

    # To handle branching
    _repo=_Repo(rw_dir+repo.repoURL)
    print("trying to access branch with name " + branch)
    print("available branches are ",_repo.heads)
    if branch not in _repo.heads:
        print("tried to checkout to branch which doesnt exist")
        print("redirecting to default branch")
        # if there are multiple branches
        if len( _repo.heads)>0:
            _repo.heads[0].checkout()
            branch=_repo.heads[0].name
        # if there is only one branch
        else:
            branch="master"
    else:
        _repo.heads[branch].checkout()
        print("repo {} has been checked out to {}".format(name,branch))

    context['repo'] = repo
    context['repo_heads'] =_repo.branches
    context['name'] = name
    context['owner'] = owner
    context['current_branch'] = branch  

    return context


def detail_repo(request, name, owner, branch="master", **kwargs):
    curDir = os.path.join(rw_dir, owner, name)
    isEmpty=False
    g = git.Git(curDir)
    try:
        g.pull('origin',branch)
    except:
        isEmpty=True
    repo = Repo.objects.filter(name=name).filter(owner__username=owner).first()
    #repo.pull('origin',branch)
    # o = repo.remotes.origin
    # o.pull()
    context = prepare_context(name, owner, branch, repo)
    teDir=''
    if('subpath' in kwargs.keys()):
        curDir = os.path.join(curDir, kwargs['subpath'])
        teDir=teDir+kwargs['subpath']
        context['subpath'] = kwargs['subpath']

    context['curDir'] = teDir
    context['forkedChild']=Repo.objects.filter(parent=repo)
    context['isEmpty']=isEmpty
    allContents = os.listdir(curDir)
    fileContents = []
    dirContents = []

    for f in allContents:
        if not str(f).endswith('.git'):
            if(os.path.isfile(os.path.join(curDir, str(f)))):
                fileContents.append(f)
            else:
                dirContents.append(f)
        print(f)

    context['fileContents'] = fileContents
    context['dirContents'] = dirContents
    context['file_view'] = False
    
    return render(request, 'Repos/repo_detail.html', context=context)


def detail_file(request, name, owner, branch="master", **kwargs):
    repo = Repo.objects.filter(name=name).filter(owner__username=owner).first()

    context = prepare_context(rw_dir, owner, branch, repo)
    curDir = os.path.join(rw_dir, owner, name)
    fileDir = os.path.join(curDir, kwargs['subpath'])

    file = open(fileDir)

    context['file_content'] = file.read()
    context['file_view'] = True

    file.close()

    return render(request, 'Repos/repo_detail.html', context=context)


def delete_repo(request, name, owner):
    context = {}
    repo = Repo.objects.filter(name=name).filter(owner__username=owner).first()
    activities = Activity.objects.filter(user=request.user, targetRepo=repo)
    for activity in activities:
        activity.delete()
    repo.delete()
    return redirect('home')

def change_visibility(request,name,owner):
    context={}
    repo = Repo.objects.filter(name=name).filter(owner__username=owner).first()
    if repo.is_private:
        repo.is_private=False
    else:
        repo.is_private=True
    repo.save()
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
        activity = Activity.objects.filter(user=request.user,targetRepo=repo)
        if len(activity)>0:
            for ac in activity:
                ac.delete()
    else:
        repo.star.add(request.user)
        activity = Activity.starredRepo(request.user,repo)
        activity.save()
        print(activity)
    context = {
        'repo': repo,
    }
    html = render_to_string('Repos/star-section.html', context, request=request)
    return JsonResponse({'html': html})

def fork(request,id):
    parent = Repo.objects.get(id=id)
    if not Repo.objects.filter(owner=request.user).filter(name=parent.name).exists():
        new_repo=Repo.objects.create(parent=parent,owner=request.user,name=parent.name,is_private=False)
        new_repo.create_fork(parent)
        new_repo.save()
        new_repo.collaborators.add(request.user)
        new_repo.save()
        activity = Activity.forkedRepo(request.user,parent.owner,parent)
        activity.save()
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

def manage_collaborators(request):
    type=request.POST.get('type')
    repoId=request.POST.get('id')
    username=request.POST.get('username')

    users=User.objects.filter(username=username)
    context={}
    if len(users) == 0:
        context['error']='User does not exist'
        return JsonResponse({'data': context})
    user=users.first()
    repo=Repo.objects.get(id=repoId)
    if type=='0':
        if user in repo.collaborators.all():
            context['message']='User already added'
        else:
            repo.collaborators.add(user)
            context['message']='User added successfully'

    if type=='1':
        if user not in repo.collaborators.all():
            context['message']='User is not added'
        else:
            repo.collaborators.remove(user)
            context['message']='User removed successfully'

    repo.save()
    html = render_to_string('Repos/repoDetailComponents/collaboratorList.html', {'repo': repo}, request=request)
    return JsonResponse({'data':context,'html':html})