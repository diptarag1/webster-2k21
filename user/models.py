from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    following = models.ManyToManyField(User,related_name='following')
    followers = models.ManyToManyField(User,related_name='followers')

    def __str__(self):
        return  self.user.username
