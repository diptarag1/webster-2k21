from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


urlpatterns=[
    path('initrepo/',views.init_Repo,name='initrepo'),
    path('<owner>/<name>/',views.detail_repo,name='detail_repo'),
    path('delete/<owner>/<name>/',views.delete_repo,name='delete_repo'),
    path('star/',views.star,name='star'),
    path('forkg/<id>/',views.forkg,name='forkg'),
    # path('<ownerUsername>/',views.TBA,name='owner-view'), #To be added
    # path('<ownerUsername>/<repoName>',views.TBA,name='repo-view'), #To be added
    path('<ownerUsername>/<repoName>/addremovecollaborator',views.add_remove_collaborator,name='add-remove-collaborator'),
]