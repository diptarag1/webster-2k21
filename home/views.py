from django.shortcuts import render
from Repos.models import Repo
from user.models import Activity
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.http import JsonResponse

# Create your views here.

def index(request):
    if request.user.is_authenticated:
        context={}
        repos=Repo.objects.filter(collaborators=request.user)
        followings=request.user.profile.following.all()
        activities=Activity.objects.filter(user__in=followings).order_by('-time')
        context['repos']=repos
        context['activities'] = activities
        return render(request,'home/index.html',context=context)
    return render(request, 'user/signin.html')

def filter_repo(request):
    context={}
    searchVal=request.POST.get('searchVal')
    context['repos']=Repo.objects.filter(collaborators=request.user).filter(name__startswith=searchVal)
    html = render_to_string('home/components/repoList.html', context=context, request=request)
    return JsonResponse({'html': html})

def filter_user(request):
    context={}
    searchVal=request.POST.get('searchVal')
    context['users']=User.objects.filter(username__startswith=searchVal)
    return JsonResponse({'data':list(context['users'])})

def error_404(request):
    data = {}
    return render(request, '404.html', data)

def error_500(request):
    data = {}
    return render(request, '500.html', data)