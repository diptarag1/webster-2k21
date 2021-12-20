from django.shortcuts import render
from Repos.models import Repo
from user.models import Activity
from django.contrib.auth.models import User

# Create your views here.

def index(request):
    if request.user.is_authenticated:
        context={}
        repos=Repo.objects.filter(owner=request.user)
        followings=request.user.profile.following.all()
        activities=Activity.objects.filter(user__in=followings).order_by('-time')
        context['repos']=repos
        context['activities'] = activities
        return render(request,'home/index.html',context=context)
    return render(request, 'user/signin.html')