from django.shortcuts import render
from Repos.models import Repo
from user.models import Activity


# Create your views here.

def index(request):
    if request.user.is_authenticated:
        context={}
        repos=Repo.objects.filter(owner=request.user)
        activities=Activity.objects.all().order_by('-time')
        context['repos']=repos
        context['activities'] = activities
        return render(request,'home/index.html',context=context)
    return render(request, 'user/signin.html')