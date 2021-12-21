from django.db import models
from django.contrib.auth.models import User
from git import Repo as gitRepo
import os, shutil
from taggit.managers import TaggableManager

from .serverLocation import rw_dir


# Create your models here.
class Repo(models.Model):
    parent = models.ForeignKey("self", null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owner')
    collaborators = models.ManyToManyField(User, related_name='collaborators', blank=True)
    repoURL = models.CharField(max_length=30)  # ownerName/repoName
    star = models.ManyToManyField(User, related_name='star', blank=True)
    is_private = models.BooleanField(default=False)

    def __str__(self):
        return self.repoURL

    def save(self, *args, **kwargs):
        gitRepo.init(os.path.join(rw_dir, self.repoURL),bare=True)
        self.repoURL = str(self.owner) + '/' + self.name
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        shutil.rmtree(os.path.join(rw_dir, self.repoURL))
        super().delete(*args, **kwargs)

    def create_fork(self, parent):
        parentGitRepo = gitRepo(os.path.join(rw_dir, parent.repoURL))
        curRepo = parentGitRepo.clone(os.path.join(rw_dir, self.repoURL))
        curRepo.delete_remote('origin')  # deleting origin remote which is automatically created


class Issue(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='author')
    repo = models.ForeignKey(Repo, on_delete=models.CASCADE, related_name='repot')
    topic = models.CharField(max_length=120)
    description = models.TextField()
    tags = TaggableManager()

    def __str__(self):
        return self.topic


