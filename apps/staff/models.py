from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

from config.constants import ROLE_CHOICES


class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, name, password=None, **extra_fields):
        if not phone_number or not name:
            raise ValueError("The Phone Number and Name fields are required")
        user = self.model(phone_number=phone_number, name=name,**extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, name, password=None,**extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(phone_number,name, password, **extra_fields)


class CustomUser(AbstractUser):
    username=None
    phone_number = models.CharField(max_length=13, unique=True)
    name = models.CharField(max_length=64, unique=True)
    role = models.CharField(max_length=13, choices=ROLE_CHOICES)
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE, related_name='store_staff', null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.name

