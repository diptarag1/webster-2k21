from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
# Create your models here.
import time
class LoginToken(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    token=models.CharField(null=True,blank=True,unique=True,max_length=20)
    creation_date = models.DateTimeField(default=timezone.now())
    expiration_seconds = models.BigIntegerField()

    def __str__(self):
        return self.user.username
