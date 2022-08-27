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
