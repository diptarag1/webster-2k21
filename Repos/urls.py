from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


urlpatterns=[
    path('initrepo/',views.init_Repo,name='initrepo'),
]