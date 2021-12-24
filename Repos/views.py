from django.shortcuts import get_object_or_404, render, redirect, HttpResponse
from rest_framework import status

from .forms import RepoCreateForm, AddCollaboratorForm, IssueCreateForm, IssueCommentCreateForm
from .models import Repo, Issue, IssueComment
from user.models import Activity
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.http import JsonResponse, HttpResponseRedirect
import os
from .serverLocation import rw_dir
from git import Git, Repo as _Repo
import git
import subprocess
import datetime
from django.contrib import messages


# Create your views here.
def init_Repo(request):
    if request.method == 'POST':
        form = RepoCreateForm(request.POST)
        if form.is_valid():
            try:
                # print(form.cleaned_data['group1'])
                new_repo_name=form.cleaned_data['rname']
                if not Repo.objects.filter(owner=request.user).filter(name=new_repo_name):
                    is_private=request.POST.get('group1')
                    if is_private == 'private':
                        is_private=True
                    else:
                        is_private=False
                    new_repo = Repo(owner=request.user, is_private=is_private, name=new_repo_name)
                    new_repo.repoURL = str(new_repo.owner) + '/' + new_repo.name
                    new_repo.save()
                    new_repo.collaborators.add(request.user)
                    new_repo.save()
                    # subprocess.call(['chmod', '-R', '777', rw_dir + new_repo.repoURL + ".git"])
                    git.Git(rw_dir + request.user.username).clone(rw_dir + new_repo.repoURL + ".git")
                    activity = Activity.createdRepo(request.user, new_repo)
                    activity.save()
                    messages.success(request, "Repo created successfully")
                    return redirect('home')
                else:
                    messages.error(request,"Repo with this name already exists")
            except:
                messages.error(request, "Repo details are invalid")
            # for now
        else:
            messages.error(request, "Repo details are invalid")
    else:
        form = RepoCreateForm()
    return render(request, 'Repos/repoCreate.html', {'form': form, 'randomUniqueName': "newDivaniRepo"})


def prepare_context(name, owner, branch, repo):
    context = {}
    # To handle branching
    _repo = _Repo(rw_dir + repo.repoURL)
    bare_repo = _Repo(rw_dir + repo.repoURL + ".git")

    print("trying to access branch with name " + branch)
    print("available branches are ", bare_repo.heads)

    isEmpty = False

    if branch not in bare_repo.heads:
        print("tried to checkout to branch which doesnt exist")
        print("redirecting to default branch")
        if len(bare_repo.heads) == 0:
            isEmpty = True
        else:
            branch = "master"
    else:
        print(branch)
        try:
            _repo.heads[branch].checkout()
            print("repo {} has been checked out to {}".format(name, branch))
        except:
            _repo.git.checkout('-b', branch)
            print("repo {} has been -b checked out to {}".format(name, branch))

    if not isEmpty:
        g = git.Git(os.path.join(rw_dir, owner, name))
        g.pull('origin', branch)

    context['repo'] = repo
    context['repo_heads'] = bare_repo.branches
    context['name'] = name
    context['owner'] = owner
    context['current_branch'] = branch
    context['isEmpty'] = isEmpty
    return context


def detail_issue(request, name, owner, issue_id, **kwargs):
    context = {}
    issue = Issue.objects.filter(id=issue_id).first()
    issue_comments = IssueComment.objects.filter(issue=issue)
    issue_comment_create_form = IssueCommentCreateForm()
    repo = Repo.objects.filter(name=name).filter(owner__username=owner).first()

    context['issue'] = issue
    context['issue_comments'] = issue_comments
    context['current_user'] = request.user.username
    context['issue_comment_create_form'] = issue_comment_create_form
    context['repo'] = repo
    return render(request, 'Repos/issue_detail.html', context=context)


def detail_repo(request, name, owner, branch="master", **kwargs):
    curDir = os.path.join(rw_dir, owner, name)
    g = git.Git(curDir)

    repo = Repo.objects.filter(name=name).filter(owner__username=owner).first()
    # repo.pull('origin',branch)
    # o = repo.remotes.origin
    # o.pull()
    context = prepare_context(name, owner, branch, repo)
    teDir = ''
    if ('subpath' in kwargs.keys()):
        curDir = os.path.join(curDir, kwargs['subpath'])
        teDir = teDir + kwargs['subpath']
        context['subpath'] = kwargs['subpath']

    context['curDir'] = teDir
    context['forkedChild'] = Repo.objects.filter(parent=repo)

    allContents = os.listdir(curDir)
    fileContents = []
    dirContents = []

    for f in allContents:
        if not str(f).endswith('.git'):
            if (os.path.isfile(os.path.join(curDir, str(f)))):
                fileContents.append(f)
            else:
                dirContents.append(f)
        print(f)

    context['fileContents'] = fileContents
    context['dirContents'] = dirContents
    context['file_view'] = False

    context['issues'] = Issue.objects.all()

    return render(request, 'Repos/repo_detail.html', context=context)


def detail_file(request, name, owner, branch="master", **kwargs):
    repo = Repo.objects.filter(name=name).filter(owner__username=owner).first()

    context = prepare_context(name, owner, branch, repo)
    curDir = os.path.join(rw_dir, owner, name)
    fileDir = os.path.join(curDir, kwargs['subpath'])

    file = open(fileDir)

    context['file_content'] = file.read()
    context['file_view'] = True

    file.close()

    return render(request, 'Repos/repo_detail.html', context=context)


def delete_repo(request, name, owner):
    context = {}
    try:
        repo = Repo.objects.filter(name=name).filter(owner__username=owner).first()
        activities = Activity.objects.filter(user=request.user, targetRepo=repo)
        for activity in activities:
            activity.delete()
        repo.delete()
        messages.success(request, "Repo deleted successfully")
    except:
        messages.error(request, "could not delete Repo")
    return redirect('home')


def change_visibility(request, name, owner):
    context = {}
    try:
        repo = Repo.objects.filter(name=name).filter(owner__username=owner).first()
        if repo.is_private:
            repo.is_private = False
        else:
            repo.is_private = True
        repo.save()
        if (repo.is_private):
            messages.success(request, "Visibility changed to private")
        else:
            messages.success(request, "Visibility changed to public")
    except:
        messages.error(request, "could not change Visibility")

    # return render(request, 'Repos/repo_detail.html', context=context)
    return redirect('detail_repo', name=name, owner=owner)


def add_remove_collaborator(request, ownerUsername, repoName):
    rName = str(ownerUsername) + '/' + repoName
    curRepo = get_object_or_404(Repo, repoURL=rName)
    if request.method == 'POST':
        form = AddCollaboratorForm(request.POST)
        if form.is_valid():
            collaborator = User.objects.filter(username=form.cleaned_data['collaboratorUsername']).first()
            if (curRepo.collaborators.filter(username=collaborator.username).exists()):
                curRepo.collaborators.remove(collaborator)
                messages.success(request, "removed collaborator")
            else:
                curRepo.collaborators.add(collaborator)
                messages.success(request, "added collaborator")
            curRepo.save()
        else:
            messages.error(request, "added collaborator")
        return redirect('detail_repo', name=repoName, owner=ownerUsername)
    else:
        form = AddCollaboratorForm()
    return render(request, 'Repos/addCollaborator.html', {'form': form})


def star(request):
    id = request.POST.get('id')
    repo = Repo.objects.get(id=id)
    context = {
        'repo': repo,
    }
    try:
        if request.user in repo.star.all():
            repo.star.remove(request.user)
            activity = Activity.objects.filter(user=request.user, targetRepo=repo)
            if len(activity) > 0:
                for ac in activity:
                    ac.delete()
            is_repo_starred = False
        else:
            repo.star.add(request.user)
            activity = Activity.starredRepo(request.user, repo)
            activity.save()
            is_repo_starred = True
            print(activity)
    except:
        return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)

    html = render_to_string('Repos/star-section.html', context, request=request)
    return JsonResponse({'html': html, 'is_repo_starred': is_repo_starred}, )


def fork(request, id):
    parent = Repo.objects.get(id=id)
    if not Repo.objects.filter(owner=request.user).filter(name=parent.name).exists():
        try:
            new_repo = Repo.objects.create(parent=parent, owner=request.user, name=parent.name, is_private=False)
            # new_repo.create_fork(parent)
            subprocess.call(
                ['git', '-C', rw_dir + request.user.username, 'clone', '--bare', rw_dir + parent.repoURL + ".git"])
            subprocess.call(['chmod', '-R', '777', rw_dir + new_repo.repoURL + ".git"])
            git.Git(rw_dir + request.user.username).clone(rw_dir + new_repo.repoURL + ".git")
            new_repo.save()
            new_repo.collaborators.add(request.user)
            new_repo.save()
            activity = Activity.forkedRepo(request.user, parent.owner, parent)
            activity.save()
            messages.success(request, "fork done")
        except:
            messages.error(request, "fork not done")
    else:
        messages.error(request, "Repo not Found")
    return redirect('home')


def create_issue(request, owner, name):
    context = {"owner": owner, "name": name}
    if request.method == 'POST':
        print(request.POST)
        try:
            form = IssueCreateForm(request.POST)
            form.instance.author = request.user
            form.instance.repo = Repo.objects.get(owner__username=owner, name=name)
            issue = form.save()
        except:
            return JsonResponse({"message": "error"}, status=status.HTTP_400_BAD_REQUEST)
        print("issue.id " + str(issue.id))
        return JsonResponse({"issue_id": issue.id, "owner": owner, "name": name})
        # redirect('detail_issue', owner=owner, name=name,issue_id=issue.id)
        # return redirect('detail_repo',owner=owner,name=name)
    return render(request, 'Repos/issue_create_form.html', context=context)


def create_issue_comment(request, owner, name, issue_id):
    context = {}
    if request.method == 'POST':
        try:
            form = IssueCommentCreateForm(request.POST)
            form.instance.author = request.user
            form.instance.issue = Issue.objects.filter(id=issue_id).first()
            form.save()
            messages.success(request, "comment created successfully")
        except:
            messages.error(request, "could not comment on issue")
        return redirect('detail_issue', owner=owner, name=name, issue_id=issue_id)


def issue_list(request, owner, name):
    context = {}
    repo = Repo.objects.get(owner__username=owner, name=name)
    issues = Issue.objects.filter(repo=repo)
    context['issues'] = issues
    return render(request, 'Repos/issues_list.html', context=context)


def manage_collaborators(request):
    type = request.POST.get('type')
    repoId = request.POST.get('id')
    username = request.POST.get('username')

    users = User.objects.filter(username=username)
    context = {}
    if len(users) == 0:
        context['error'] = 'User does not exist'
        return JsonResponse({'data': context})
    user = users.first()
    repo = Repo.objects.get(id=repoId)
    if type == '0':
        if user in repo.collaborators.all():
            context['message'] = 'User already added'
        else:
            repo.collaborators.add(user)
            context['message'] = 'User added successfully'

    if type == '1':
        if user not in repo.collaborators.all():
            context['message'] = 'User is not added'
        else:
            repo.collaborators.remove(user)
            context['message'] = 'User removed successfully'

    repo.save()
    html = render_to_string('Repos/repoDetailComponents/collaboratorList.html', {'repo': repo}, request=request)
    return JsonResponse({'data': context, 'html': html})


