from django.shortcuts import render
from Repos.models import Repo, Activity


# Create your views here.

def index(request):
    if request.user.is_authenticated:
        context={}
        repos=Repo.objects.filter(owner=request.user)
        activities=Activity.objects.all()
        context['repos']=repos
        context['activities'] = activities
        return render(request,'home/index.html',context=context)
    return render(request, 'user/signin.html')