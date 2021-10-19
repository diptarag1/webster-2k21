from django.urls import path,re_path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('initrepo/', views.init_Repo, name='initrepo'),
    path('fork/<owner>/<name>/', views.fork, name='fork'),
    path('delete/<owner>/<name>/', views.delete_repo, name='delete_repo'),
    path('star/', views.star, name='star'),
    path('<owner>/<name>/issues/', views.issue_list, name='issue_list'),
    path('<owner>/<name>/issues/new/', views.create_issue, name='create_issue'),
    path('<ownerUsername>/<repoName>/addremovecollaborator', views.add_remove_collaborator,
         name='add-remove-collaborator'),
    path('<owner>/<name>/', views.detail_repo, name='detail_repo'),
    re_path(r'^(?P<owner>[^/]+)/(?P<name>[^/]+)/(?P<subpath>)/$', views.detail_repo, name='detail_repo1'),
    path('<owner>/<name>/<path:subpath>/', views.detail_repo, name='detail_repo2'),
]
