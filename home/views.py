from django.shortcuts import render
from Repos.models import Repo
# Create your views here.

def index(request):
    context={}
    repos=Repo.objects.filter(owner=request.user)
    context['repos']=repos
    return render(request,'home/index.html',context=context)