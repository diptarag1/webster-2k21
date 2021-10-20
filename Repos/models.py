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
        gitRepo.init(os.path.join(rw_dir, self.repoURL))
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


class Activity(models.Model):
    thisGuy = models.ForeignKey(User, null=False, on_delete=models.CASCADE, related_name='thisGuy')
    activity_type = models.SmallIntegerField()
    thatGuy = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='thatGuy')
    thatRepo = models.ForeignKey(Repo, null=True, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def createdRepo(thisGuy, thatRepo):
        return Activity(thisGuy=thisGuy, activity_type=1, thatGuy=None, thatRepo=thatRepo)

    @staticmethod
    def forkedRepo(thisGuy, thatGuy, thatRepo):
        return Activity(thisGuy=thisGuy, activity_type=2, thatGuy=thatGuy, thatRepo=thatRepo)

    @staticmethod
    def starredRepo(thisGuy, thatRepo):
        return Activity(thisGuy=thisGuy, activity_type=3, thatGuy=thatRepo.owner, thatRepo=thatRepo)

    @staticmethod
    def startedFollowing(thisGuy, thatGuy):
        return Activity(thisGuy=thisGuy, activity_type=4, thatGuy=thatGuy, thatRepo=None)

    def __str__(self):
        if self.activity_type == 1:
            return self.thisGuy.username + " created repository " + self.thatRepo.name + " on "
        if self.activity_type == 2:
            return self.thisGuy.username + " forked repository " + self.thatGuy.username + "/" + self.thatRepo.name + " on "
        if self.activity_type == 3:
            return self.thisGuy.username + " started following  " + self.thatGuy.username + " on "
        if self.activity_type == 4:
            return self.thisGuy.username + " starred " + self.thatGuy.username + "/" + self.thatRepo.name + " on "
        return "some error"
