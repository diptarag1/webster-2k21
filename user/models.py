from django.db import models
from django.contrib.auth.models import User
# Create your models here.
from django import forms
from Repos.models import Repo

class Profile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    bio = models.TextField(null=True,blank=True,default='')
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    following = models.ManyToManyField(User,related_name='following',blank=True,null=True)
    followers = models.ManyToManyField(User,related_name='followers',blank=True,null=True)
    def __str__(self):
        return  self.user.username

# Activity model to store all kind of actions performed to be showed on main screen
# example user forked react repo,user starred react repo,user followed other user

class Activity(models.Model):
    Activity_types = (
        (1, "created repository"),
        (2, "forked repository"),
        (3, "started following "),
        (4, "starred "),
    )
    user = models.ForeignKey(User, null=False, on_delete=models.CASCADE, related_name='actor')
    activity_type = models.SmallIntegerField(null=False)
    targetUser = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='target')
    targetRepo = models.ForeignKey(Repo, null=True, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def createdRepo(user, targetRepo):
        return Activity(user=user, activity_type=1, targetUser=None, targetRepo=targetRepo)

    @staticmethod
    def forkedRepo(user, targetUser, targetRepo):
        return Activity(user=user, activity_type=2, targetUser=targetUser, targetRepo=targetRepo)

    @staticmethod
    def starredRepo(user, targetRepo):
        return Activity(user=user, activity_type=3, targetUser=targetRepo.owner, targetRepo=targetRepo)

    @staticmethod
    def startedFollowing(user, targetUser):
        return Activity(user=user, activity_type=4, targetUser=targetUser, targetRepo=None)

    def __str__(self):
        if self.activity_type == 1:
            return self.user.username + " created repository " + self.targetRepo.name + " on "
        if self.activity_type == 2:
            return self.user.username + " forked repository " + self.targetUser.username + "/" + self.targetRepo.name + " on "
        if self.activity_type == 3:
            return self.user.username + " started following  " + self.targetUser.username + " on "
        if self.activity_type == 4:
            return self.user.username + " starred " + self.targetUser.username + "/" + self.targetRepo.name + " on "
        return "some error"

