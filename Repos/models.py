from django.db import models
from django.contrib.auth.models import User
from git import Repo as gitRepo
import os

rw_dir = '~/git_test_repos'

# Create your models here.
class Repo(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owner')
    collaborators = models.ManyToManyField(User, related_name='collaborator',blank=True)
    repoURL = models.CharField(max_length=30) #ownerName/repoName

    def __str__(self):
        return self.repoURL 

    def save(self, *args, **kwargs):
        gitRepo.init(os.path.join(rw_dir, self.repoURL))
        super().save(*args, **kwargs)

    