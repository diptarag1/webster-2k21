from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.utils.encoding import force_bytes,force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .tokens import account_activation_token
from .models import LoginToken
from django.utils import timezone
from django.contrib import messages
# Create your views here.
def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        # return redirect('home')
        return HttpResponse('Thank you for your email confirmation. Now you can login your account.')
    else:
        return HttpResponse('Activation link is invalid!')

def two_factor_login(request):
    if request.method=='POST':
        token=request.POST.get('token')
        print(token)
        try:
            user_token=LoginToken.objects.get(token=token)
            print(user_token.user)
            if (timezone.now()-user_token.creation_date).seconds >= 600:
                user_token.delete()
                return HttpResponse('Token has been expired')
            user=user_token.user
            user_token.delete()
            login(request, user)
            return redirect('home')
        except:
            return HttpResponse('Invalid Token')
    else:
        return render(request,'user/verify.html')