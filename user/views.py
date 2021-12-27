import random
from .forms import ProfileUpdateForm,UserUpdateForm
from django.contrib import messages
from django.contrib.auth import login, authenticate,logout
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from .forms import SignUpForm
from django.template.loader import render_to_string
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.contrib.auth.models import User
from  django.http import HttpResponse
from Repos.models import Repo
from .models import Profile,Activity
from .userAdd import add_user
from os import mkdir
from Repos.serverLocation import rw_dir
from django.shortcuts import get_object_or_404
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from home.views import error_404
from verify.tokens import account_activation_token
from django.utils.crypto import get_random_string
from verify.models import LoginToken
# Create your views here.

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            mail_subject = 'Activate your account.'
            message = render_to_string('acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            email.send()
            try:
                mkdir(rw_dir+str(user))
            except:
                print("could not make directory")
            # add_user(username=username,password=raw_password)
            return redirect('signin')
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
                return HttpResponse("not active")
            elif user is not None:
                # try:
                #     user_token=LoginToken.objects.get(user=user)
                # except:
                #     user_token=LoginToken.objects.create(user=user,token=get_random_string(20))
                # current_site = get_current_site(request)
                # mail_subject = 'Token to login your account.'
                # message = render_to_string('login_email.html', {
                #     'user': user,
                #     'domain': current_site.domain,
                #     'token': account_activation_token.make_token(user),
                # })
                # to_email = User.objects.get(user=user).email
                # email = EmailMessage(
                #     mail_subject, message, to=[to_email]
                # )
                # email.send()
                login(request, user)
                return redirect('home')
            else:
                return HttpResponse("password incorrect")
        else:
            return HttpResponse("username does not exist")
    return render(request, 'user/signin.html')

def signout(request):
    logout(request)
    return redirect('home')

def profile(request,uname):
    context={}
    user=get_object_or_404(User,username=uname)
    userProfile=Profile.objects.get(user=user)
    context['user']=user
    context['userProfile']=userProfile
    context['repos']=Repo.objects.filter(owner__username=uname)
    context['mostPopularRepos']=Repo.objects.filter(owner__username=uname)[0:6]
    context['activity'] = [2 for i in range(45*7)]
    context['profileForm']=ProfileUpdateForm(instance=request.user.profile)
    context['userForm']=UserUpdateForm(instance=request.user)
    return render(request, 'user/profile_detail.html', context=context)

def follow(request):
    pro_user=request.POST.get('user')
    profile= Profile.objects.get(user__username=pro_user)
    cprofile=Profile.objects.get(user=request.user)
    pro_user=User.objects.get(username=pro_user)
    context={}
    context['user']=pro_user
    if request.user in profile.followers.all():
        profile.followers.remove(request.user)
        cprofile.following.remove(pro_user)
        activity=Activity.objects.filter(activity_type=4,user=request.user,targetUser=pro_user)
        if len(activity)>0:
            activity[0].delete()
        message="Unfollowed Successfully"
    else:
        profile.followers.add(request.user)
        cprofile.following.add(pro_user)
        activity=Activity.objects.create(activity_type=4,user=request.user,targetUser=pro_user,targetRepo=None)
        # print(activity)
        activity.save()
        message="Followed Successfully"
    html = render_to_string('user/follow_section.html', context, request=request)
    return JsonResponse({'html': html, 'message': message})

def edit_profile(request):
    if request.user.is_authenticated:
        if (request.method == 'POST'):
            p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
            u_form = UserUpdateForm(request.POST,instance=request.user)
            if True:
                p_form.save()
                u_form.is_valid()
                print(p_form.cleaned_data['bio'])
                messages.success(request, 'Account has been updated.')
                return redirect('profile', uname=request.user.username)
        else:
            # p_form = ProfileUpdateForm(instance=request.user.profile)
            pass
    return redirect('home')