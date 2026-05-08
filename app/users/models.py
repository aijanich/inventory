from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models


class CustomUserManager(UserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("role", "client")
        return super().create_user(username, email=email, password=password, **extra_fields)

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        # Django's createsuperuser management command uses this path.
        # Ensure our required "role" field is set sensibly for superusers.
        extra_fields.setdefault("role", "admin")
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return super().create_superuser(username, email=email, password=password, **extra_fields)


class User(AbstractUser):
    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("client", "Client"),
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="client")

    objects = CustomUserManager()

    def __str__(self):
        return self.username
