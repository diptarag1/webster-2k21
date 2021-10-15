from django.db import models
from django.contrib.auth.models import User
from git import Repo as gitRepo
import os

rw_dir = '~/git_test_repos'

# Create your models here.
class Repo(models.Model):
    parent=models.ForeignKey("self",null=True,on_delete=models.CASCADE)
    name=models.CharField(max_length=30)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owner')
    collaborators = models.ManyToManyField(User, related_name='collaborators',blank=True)
    repoURL = models.CharField(max_length=30) #ownerName/repoName
    star = models.ManyToManyField(User,related_name='star',blank=True)

    def __str__(self):
        return self.repoURL 

    def save(self, *args, **kwargs):
        gitRepo.init(os.path.join(rw_dir, self.repoURL))
        self.repoURL=str(self.owner) + '/' + self.name
        super().save(*args, **kwargs)

    