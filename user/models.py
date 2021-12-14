from django.db import models
from django.contrib.auth.models import User
# Create your models here.
from Repos.models import Repo

class Profile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    following = models.ManyToManyField(User,related_name='following')
    followers = models.ManyToManyField(User,related_name='followers')
    def __str__(self):
        return  self.user.username

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

