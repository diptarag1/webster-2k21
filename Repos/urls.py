from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('initrepo/', views.init_Repo, name='initrepo'),
    path('fork/<id>/', views.fork, name='fork'),
    path('<owner>/<name>/issues/', views.issue_list, name='issue_list'),
    path('<owner>/<name>/issues/new/', views.create_issue, name='create_issue'),
    path('<owner>/<name>/', views.detail_repo, name='detail_repo'),
    path('<owner>/<name>/', views.detail_repo, name='detail_repo1'),
    path('<owner>/<name>/<subpath>', views.detail_repo, name='detail_repo2'),
    path('delete/<owner>/<name>/', views.delete_repo, name='delete_repo'),
    path('star/', views.star, name='star'),
    path('<ownerUsername>/<repoName>/addremovecollaborator', views.add_remove_collaborator,
         name='add-remove-collaborator'),
]
