from django.urls import path,re_path
from django.contrib.auth import views as auth_views
from . import views


urlpatterns=[
path('activate/<uidb64>/<token>/', views.activate, name='activate'),
path('login_token/',views.two_factor_login,name='two_factor'),
]