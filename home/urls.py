from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


urlpatterns=[
    path('',views.index,name='home'),
    path('filterRepo/',views.filter_repo,name='filter_repo'),
    path('filterUser/',views.filter_user,name='filter_user'),
]