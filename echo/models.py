from importlib.metadata import requires

from django.db import models
from django.contrib.auth.models import UserManager, AbstractBaseUser, PermissionsMixin
from django.utils import timezone

# Create your models here.

class CustomUserManager(UserManager):
    def _create_user(self, username, password, **extra_fields):
        if not username:
            raise ValueError("You have not provided a valid username")

        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        
        return user
        
    def create_user(self, username=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, password, **extra_fields)
    
    def create_superuser(self, username=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must be assigned to is_staff=True.')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must be assigned to is_superuser=True.')

        return self._create_user(username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(blank=True, default='', unique=True)
    name = models.CharField(max_length=255, blank=True, default='')

    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(blank=True, null=True)

    objects = CustomUserManager()


    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []


    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.username

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name or self.username


class Books(models.Model):
    name = models.CharField(max_length=30)
    author = models.CharField(max_length=20)
    price = models.IntegerField()

