from datetime import time, timezone

from django.db import models
from django.contrib.auth.models import User
from git import Repo as gitRepo
import os, shutil
from taggit.managers import TaggableManager
from .serverLocation import rw_dir, new_dir
import subprocess


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
        gitRepo.init(os.path.join(new_dir, self.repoURL) + ".git", bare=True)
        self.repoURL = str(self.owner) + '/' + self.name
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        shutil.rmtree(os.path.join(rw_dir, self.repoURL))
        super().delete(*args, **kwargs)

    def create_fork(self, parent):
        parentGitRepo = gitRepo(os.path.join(rw_dir, parent.repoURL))
        subprocess.call(['git', 'clone', '--bare', rw_dir + parent.repoURL + ".git"])
        # curRepo = parentGitRepo.clone(os.path.join(rw_dir, self.repoURL))
        # curRepo.delete_remote('origin')  # deleting origin remote which is automatically created


class Issue(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='author')
    repo = models.ForeignKey(Repo, on_delete=models.CASCADE, related_name='repot')
    topic = models.CharField(max_length=120)
    is_open = models.BooleanField(default=True)
    assignees = models.ManyToManyField(User, related_name='assignees', blank=True)
    description = models.TextField()
    posted_on = models.DateTimeField(auto_now_add=True)
    tags = TaggableManager()
    def close_issue(self):
        self.is_open=False
        self.save()

    def __str__(self):
        return self.topic


class IssueComment(models.Model):
    author = models.ForeignKey(User, null=False, on_delete=models.CASCADE, related_name='comment_author')
    issue = models.ForeignKey(Issue, null=False, on_delete=models.CASCADE, related_name='comment_issue')
    data = models.TextField()
    posted_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return " "


class PullRequest(models.Model):
    author = models.ForeignKey(User, null=False, on_delete=models.CASCADE, related_name='request_author')
    base_repo = models.ForeignKey(Repo, on_delete=models.CASCADE, related_name='base_repo')
    base_branch = models.CharField(max_length=120)
    feature_repo = models.ForeignKey(Repo, on_delete=models.CASCADE, related_name='feature_repo')
    feature_branch = models.CharField(max_length=120)

    def __str__(self):
        return "Merging " + str(self.feature_repo) + "/" + self.feature_branch + " into " + str(self.base_repo) + "/" + self.base_branch

 
