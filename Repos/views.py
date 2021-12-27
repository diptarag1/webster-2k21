from datetime import datetime
from django.shortcuts import render, redirect
from rest_framework import status
from django.shortcuts import get_object_or_404
from .forms import PullRequestCreateForm, RepoCreateForm, AddCollaboratorForm, IssueCreateForm, IssueCommentCreateForm
from .models import PullRequest, Repo, Issue, IssueComment
from user.models import Activity
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.http import JsonResponse
import os
from .serverLocation import rw_dir
from git import Repo as _Repo
import git
import subprocess
from django.contrib import messages


# Create your views here.
from .utility import get_bare_repo_by_name, get_nonbare_repo_by_name


def init_Repo(request):
    if request.method == 'POST':
        form = RepoCreateForm(request.POST)
        if form.is_valid():
            try:
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
                    subprocess.call(['chmod', '-R', '777', rw_dir + new_repo.repoURL + ".git"])
                    git.Git(rw_dir + request.user.username).clone(rw_dir + new_repo.repoURL + ".git")
                    if not is_private:
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
    _repo = get_nonbare_repo_by_name(owner, name)
    bare_repo = get_bare_repo_by_name(owner, name)
    isEmpty = False

    if branch not in bare_repo.heads:
        if len(bare_repo.heads) == 0:
            isEmpty = True
        else:
            branch = "master"
    else:
        try:
            _repo.heads[branch].checkout()
        except:
            _repo.git.checkout('-b', branch)

    if not isEmpty:
        g = git.Git(os.path.join(rw_dir, owner, name))
        g.pull('origin', branch)

    repo = get_object_or_404(Repo, repoURL=owner+'/'+name)
    pull_requests = PullRequest.objects.filter(base_repo=repo)

    context['repo'] = repo
    context['repo_heads'] = bare_repo.branches
    context['name'] = name
    context['owner'] = owner
    context['current_branch'] = branch
    context['isEmpty'] = isEmpty
    context['pull_requests'] = pull_requests
    return context


def detail_issue(request, name, owner, issue_id, **kwargs):
    context = {}
    issue = Issue.objects.filter(id=issue_id).first()
    issue_comments = IssueComment.objects.filter(issue=issue)
    issue_comment_create_form = IssueCommentCreateForm()
    repo = Repo.objects.filter(name=name).filter(owner__username=owner).first()
    assignees=[user for user in issue.assignees.all()]

    context['issue'] = issue
    context['issue_comments'] = issue_comments
    context['current_user'] = request.user.username
    context['issue_comment_create_form'] = issue_comment_create_form
    context['repo'] = repo
    context['assignees'] = assignees

    return render(request, 'Repos/issue_components/issue_detail.html', context=context)


def detail_repo(request, name, owner, branch="master", **kwargs):
    curDir = os.path.join(rw_dir, owner, name)
    repos = Repo.objects.filter(name=name).filter(owner__username=owner)
    repo = get_object_or_404(repos)
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

    context['fileContents'] = fileContents
    context['dirContents'] = dirContents
    context['file_view'] = False

    context['issues'] = Issue.objects.filter(repo=repo)

    return render(request, 'Repos/repo_components/repo_detail.html', context=context)


def detail_file(request, name, owner, branch="master", **kwargs):
    repo = Repo.objects.filter(name=name).filter(owner__username=owner).first()
    context = prepare_context(name, owner, branch, repo)
    curDir = os.path.join(rw_dir, owner, name)
    fileDir = os.path.join(curDir, kwargs['subpath'])
    file = open(fileDir)
    context['file_content'] = file.read()
    context['file_view'] = True

    file.close()

    return render(request, 'Repos/repo_components/repo_detail.html', context=context)

def commit_list(request, name, owner, branch="master", **kwargs):
    curDir = os.path.join(rw_dir, owner, name)
    g = git.Git(curDir)

    repos = Repo.objects.filter(name=name).filter(owner__username=owner)
    repo = get_object_or_404(repos)
    _repo = _Repo(rw_dir + repo.repoURL)
    context = prepare_context(name, owner, branch, repo)

    commits = list(_repo.iter_commits(branch))
    for commit in commits:
        commit.authored_date=datetime.fromtimestamp(commit.authored_date)
    # print([datetime.fromtimestamp(commit.authored_date)  for commit in commits])
    context['commits'] = commits
    context['commit_view'] = True

    return render(request, 'Repos/repo_components/repo_detail.html', context=context)

def delete_repo(request, name, owner):
    context = {}
    try:
        repo = Repo.objects.filter(name=name).filter(owner__username=owner).first()
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
    return render(request, 'Repos/add_collaborator.html', {'form': form})


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
            _non_bare_repo = _Repo(rw_dir + new_repo.repoURL)
            _non_bare_repo.create_remote('bare_parent', rw_dir + parent.repoURL + ".git")
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


def issue_close(request, issue_id):
    repo=None
    try :
        if request.method != 'POST':
            raise Exception('INVALID method')
        query_set = Issue.objects.filter(id=issue_id)
        if len(query_set) == 0:
            raise Exception("issue does not exist")
        issue = query_set.first()
        repo = issue.repo
        if request.user not in repo.collaborators.all():
            raise Exception("You so not have the authority to close this issue")
        if  issue.is_open==False:
            raise Exception("Issue is already closed")
        issue.is_open = False
        issue.save()
        messages.success(request, "ISSUE closed successfully")
    except Exception as error:
        messages.error(request, str(error))
    finally:
        if(repo is None):
            return redirect('home')
        owner=repo.owner
        name=repo.name
        return redirect('detail_issue', owner=owner, name=name, issue_id=issue_id)

def issue_edit(request, issue_id):
    repo=None
    try :
        if request.method != 'POST':
            raise Exception('INVALID method')
        query_set = Issue.objects.filter(id=issue_id)
        if len(query_set) == 0:
            raise Exception("issue does not exist")
        issue = query_set.first()
        repo = issue.repo
        if request.user != issue.author and request.user not in repo.collaborators.all():
            raise Exception("You so not have the authority to edit issue")
        new_topic_name = request.POST.get('issue_edit_box')
        issue.topic = new_topic_name
        issue.save()
        messages.success(request, "ISSUE edited successfully")
    except Exception as error:
        messages.error(request, str(error))
    finally:
        if(repo is None):
            return redirect('home')
        owner=repo.owner
        name=repo.name
        return redirect('detail_issue', owner=owner, name=name, issue_id=issue_id)

def create_issue(request, owner, name):
    context = {"owner": owner, "name": name}
    query_set=Repo.objects.filter(owner__username=owner, name=name)
    if(len(query_set)==0):
        return JsonResponse({"message": "Repo does not exist"}, status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'POST' :
        try:
            form = IssueCreateForm(request.POST)
            form.instance.author = request.user
            form.instance.repo = Repo.objects.get(owner__username=owner, name=name)
            issue = form.save()
        except:
            return JsonResponse({"message": "error"}, status=status.HTTP_400_BAD_REQUEST)
        return JsonResponse({"issue_id": issue.id, "owner": owner, "name": name})
        # redirect('detail_issue', owner=owner, name=name,issue_id=issue.id)
        # return redirect('detail_repo',owner=owner,name=name)
    return render(request, 'Repos/issue_components/issue_create_form.html', context=context)


def issue_comment_delete(request, issue_comment_id):
    issue=None
    try:
        if request.method != 'POST':
            raise Exception('INVALID method')
        query_set = IssueComment.objects.filter(id=issue_comment_id)
        if len(query_set) == 0:
            raise Exception("issue does not exist")
        comment = query_set.first()
        issue=comment.issue
        if request.user != comment.author :
            raise Exception("You so not have the authority to delete this comment")
        comment.delete()
        messages.success(request, "comment  deleted successfully")
    except Exception as error:
        messages.error(request, str(error))
    finally:
        if (issue is None):
            return redirect('home')
        repo=issue.repo
        owner = repo.owner
        name = repo.name
        return redirect('detail_issue', owner=owner, name=name, issue_id=issue.id)

def create_issue_comment(request, issue_id):
    repo=None
    try:
        if request.method != 'POST':
            raise Exception("INVALID HTTP METHOD")
        query_set=Issue.objects.filter(id=issue_id)
        if(len(query_set)==0):
            raise Exception("issue does not exist")
        issue=query_set.first()
        repo=issue.repo
        form = IssueCommentCreateForm(request.POST)
        form.instance.author = request.user
        form.instance.issue = issue
        if not form.is_valid:
            raise Exception("Form not Valid")
        form.save()
        messages.success(request, "comment created successfully")
    except Exception as error:
        messages.error(request, str(error))
    finally:
        if(repo is None):
            redirect('home')
        else:
            return redirect('detail_issue', owner=repo.owner, name=repo.name, issue_id=issue_id)

def filter_issue(request,owner,name):
    html=""
    context = {}
    try:
        tags = request.POST.get('tags')
        tags = tags.split('close')
        if(len(tags)>0):
            if(len(tags[-1])==0):
                tags.pop()
        repo =Repo.objects.get(owner__username=owner, name=name)
        if repo is None :
            raise Exception("Repo does not exist")
        if len(tags[0]) == 0:
            issues = Issue.objects.filter(repo=repo)
        else:
            issues = Issue.objects.filter(repo=repo, tags__name__in=tags).distinct()
        context['issues'] = issues
        context['repo'] = repo
        html = render_to_string('Repos/issue_components/issues_list.html', context=context, request=request)
    except Exception as error:
        messages.error(request, str(error))
    finally:
        return JsonResponse({'html': html})

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
        elif user==repo.owner:
             context['message'] = 'Cannot remove owner'
        else:
            repo.collaborators.remove(user)
            context['message'] = 'User removed successfully'

    repo.save()
    html = render_to_string('Repos/repo_components/collaborator_list.html', {'repo': repo}, request=request)
    return JsonResponse({'data': context, 'html': html})



def create_pull_request(request, owner, name):
    print("got post create_pull_request")
    try:
        context={}
        rName = str(owner) + '/' + name
        curRepo = get_object_or_404(Repo, repoURL=rName)
        print(curRepo.parent)
        _curRepo = get_bare_repo_by_name(owner, name)
        baseRepo = curRepo
        _baseRepo = _curRepo
        if request.method == 'POST':
            form = PullRequestCreateForm(request.POST)
            parentBit=(request.POST.get('parentBit')=='1')
            if not form.is_valid():
                raise Exception("Entered Details are invalid")
            if parentBit:
                print("got a forked repo as base")
                baseRepo = curRepo.parent
                _baseRepo = get_bare_repo_by_name(baseRepo.owner, name)
            if form.cleaned_data['feature_branch'] not in _curRepo.heads:
                raise Exception("feature_branch is not in current repo")
            if form.cleaned_data['base_branch'] not in _baseRepo.heads:
                raise Exception("base_branch is not in base Repo ")
            form.instance.base_repo = baseRepo
            form.instance.feature_repo = curRepo
            form.instance.author = request.user
            form.save()
            messages.success(request, "pull request created")
            return redirect('detail_repo', name=name, owner=owner)
        else:
            branches = _curRepo.branches
            repo_model_object = Repo.objects.get(owner__username=owner, name=name)
            is_repo_forked= repo_model_object.parent is not None
            parent_repo_model_object= repo_model_object.parent

            context['repo_model_object'] = repo_model_object
            context['parent_repo_model_object'] = parent_repo_model_object
            context['is_repo_forked'] = is_repo_forked
            context['branches'] = branches
    except Exception as error:
        messages.error(request, str(error))
        return redirect('home')
    return render(request, 'Repos/pull_request_components/pull_request_create.html', context)



def pull_request_detail(request, owner, name, id):
    context = {}
    pullreq = PullRequest.objects.get(id=id)
    print(pullreq)
    context['pr'] = pullreq

    cur_repo = get_bare_repo_by_name(pullreq.feature_repo.owner, pullreq.feature_repo.name)
    print(rw_dir + str(owner) + '/' + name)
    cur_nb_repo = get_nonbare_repo_by_name(pullreq.feature_repo.owner, pullreq.feature_repo.name)
    base_repo = get_bare_repo_by_name(pullreq.base_repo.owner, pullreq.base_repo.name)
    base_commit =  cur_repo.merge_base(cur_repo.commit(pullreq.base_branch), cur_repo.commit(pullreq.feature_branch))[0]
    if base_repo != cur_repo:
        for branch in cur_repo.branches:
            cur_nb_repo.git.pull('origin', branch)
        subprocess.call(['git','-C',rw_dir+str(pullreq.feature_repo.owner)+'/'+pullreq.feature_repo.name,'fetch','bare_parent'])
        base_commit = cur_nb_repo.merge_base(cur_nb_repo.commit('bare_parent/' + pullreq.base_branch), cur_nb_repo.commit(pullreq.feature_branch))[0]

    print(base_commit.message)
    context['base_commit'] = base_commit
    current_commit = cur_nb_repo.commit(pullreq.feature_branch)
    unmerged_commits = []
    while not current_commit == base_commit:
        unmerged_commits.append(current_commit)
        try:
            current_commit = current_commit.parents[0]
        except:
            print(current_commit.message)
            return redirect('home')

    print(unmerged_commits)
    context['unmerged_commits'] = unmerged_commits
    context['id'] = id

    context['name'] = name
    context['owner'] = owner

    return render(request, 'Repos/pull_request_components/pull_request_detail.html', context = context)


def commit_pull_request(request, owner, name, id):
    pullreq = PullRequest.objects.get(id=id)
    base_repo = get_bare_repo_by_name(owner, name)
    base_nb_repo = get_nonbare_repo_by_name(owner, name)
    feature_repo = get_bare_repo_by_name(pullreq.feature_repo.owner, pullreq.feature_repo.name)

    base_nb_repo.git.checkout(pullreq.base_branch)
    url = rw_dir + str(pullreq.feature_repo.owner) + '/' + pullreq.feature_repo.name + '.git'
    base_nb_repo.git.pull(url, feature_repo.heads[pullreq.feature_branch])

    base_nb_repo.git.push('origin', pullreq.base_branch)


    pullreq.delete()

    return redirect('detail_repo', name=name, owner=owner)