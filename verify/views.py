from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .tokens import account_activation_token
from .models import LoginToken
from django.utils import timezone
# Create your views here.
def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
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
        try:
            user_token=LoginToken.objects.get(token=token)
            if timezone.now()-user_token.creation_date >= 600:
                user_token.delete()
                return HttpResponse('Token has been expired')
            user=user_token.user
            user_token.delete()
            login(request, user)
            return redirect('home')
        except:
            return HttpResponse('Invalid Token')