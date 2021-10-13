from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


urlpatterns=[
    path('signup/',views.signup,name='signup'),
    path('profile/<uname>/',views.profile,name='profile'),
    path('follow/',views.follow,name='follow'),
]