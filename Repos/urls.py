from django.urls import path,re_path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('initrepo/', views.init_Repo, name='initrepo'),
    path('fork/<id>/', views.fork, name='fork'),
    path('delete/<owner>/<name>/', views.delete_repo, name='delete_repo'),
    path('change_visibility/<owner>/<name>/',views.change_visibility,name='change_visibility'),
    path('star/', views.star, name='star'),
    path('comment/delete/<issue_comment_id>/', views.issue_comment_delete, name='issue_comment_delete'),
    path('issues/edit/<issue_id>', views.issue_edit, name='issue_edit'),
    path('<owner>/<name>/issues/filter', views.filter_issue, name='filter_issue'),
    path('issues/close/<issue_id>', views.issue_close, name='issue_close'),
    path('issues/<issue_id>/comment/new/', views.create_issue_comment, name='create_issue_comment'),
    path('<owner>/<name>/issues/<issue_id>', views.detail_issue, name='detail_issue'),

    path('<owner>/<name>/issues/new/', views.create_issue, name='create_issue'),

    path('<ownerUsername>/<repoName>/addremovecollaborator/', views.add_remove_collaborator,
         name='add-remove-collaborator'),
         
    path('<owner>/<name>/view/<branch>/<path:subpath>/', views.detail_file, name='detail_file'),
    path('<owner>/<name>/view/<branch>/<path:subpath>/', views.detail_file, name='detail_file'),
    path('<owner>/<name>/', views.detail_repo, name='detail_repo'),

    path('<owner>/<name>/<branch>/', views.detail_repo, name='detail_repo1'),
    path('<owner>/<name>/<branch>/<path:subpath>/', views.detail_repo, name='detail_repo2'),
    path('manage-collaborators/',views.manage_collaborators,name='manage_collaborators'),
]
