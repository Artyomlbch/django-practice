from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Books(models.Model):
    name = models.CharField(max_length=30)
    author = models.CharField(max_length=20)
    price = models.IntegerField()

class MyUser(models.Model):
    login = models.CharField(max_length=30)
    password = models.CharField(max_length=254)
    email = models.EmailField(max_length=70)
    name = models.CharField(max_length=40)
    role = models.CharField(max_length=10)