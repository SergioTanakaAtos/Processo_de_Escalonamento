from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
# Create your models here.
class Client(models.Model):
    client_name = models.CharField(max_length=100)
    escalar = models.BooleanField(default=False)
    pass 

