from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


urlpatterns=[
    path('initrepo/',views.init_Repo,name='initrepo'),
    # path('<ownerUsername>/',views.TBA,name='owner-view'), #To be added
    # path('<ownerUsername>/<repoName>',views.TBA,name='repo-view'), #To be added
    path('<ownerUsername>/<repoName>/addremovecollaborator',views.add_remove_collaborator,name='add-remove-collaborator'),
]