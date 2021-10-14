from django.contrib.auth import login, authenticate,logout
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from .forms import SignUpForm
from django.contrib.auth.models import User
from  django.http import HttpResponse
# Create your views here.

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'user/signup.html', {'form': form})

def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        cuser = User.objects.filter(username=username)
        if len(cuser) == 1:
            if not cuser[0].is_active:
                return HttpResponse("hi")
            elif user is not None:
                login(request, user)
                return redirect('home')
            else:
                return HttpResponse("hi")
        else:
            return HttpResponse("hi")
    return render(request, 'user/signin.html')

def signout(request):
    logout(request)
    return redirect('home')

def profile(request,uname):
    context={}
    user=User.objects.get(username=uname)
    context['user']=user
    return render(request,'user/profile.html',context=context)

def follow(request):
    pass

def following(request):
    pass