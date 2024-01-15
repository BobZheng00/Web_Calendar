from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
# Create your models here.


class UserEvents(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.CharField(max_length=200)
    date = models.DateField(null=True, blank=True)
    beginning = models.IntegerField(default=0)
    end = models.IntegerField(default=0)
    description = models.TextField(default='')
    is_private = models.BooleanField(default=False)
    hex_color = models.CharField(max_length=7, default='#000000')


class Follower(models.Model):
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name="requester")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="receiver")
    is_agreed = models.BooleanField(default=False)
    allowed_access = models.BooleanField(default=False)
