from django.shortcuts import render, redirect
from .forms import RepoCreateForm
from .models import Repo

# Create your views here.
def init_Repo(request):
    if request.method == 'POST':
        form = RepoCreateForm(request.POST)
        if form.is_valid():
            new_repo = Repo(owner = request.user, repoURL = form.cleaned_data['rname'])
            new_repo.repoURL = str(new_repo.owner) + '/' + new_repo.repoURL
            new_repo.save()
            return redirect('home') #for now
    else:
        form = RepoCreateForm()
    return render(request, 'Repos/repoCreate.html', {'form': form})