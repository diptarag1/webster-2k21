from django.shortcuts import render
from Repos.models import Repo
# Create your views here.

def index(request):
    if request.user.is_authenticated:
        context={}
        repos=Repo.objects.filter(owner=request.user)
        context['repos']=repos
        return render(request,'home/index.html',context=context)
    return render(request, 'user/signin.html')