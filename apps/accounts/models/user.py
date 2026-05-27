"""Custom user model with 2FA support."""
from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.core.models.base import UUIDModel


class User(UUIDModel, AbstractUser):
    """Extended user with TOTP 2FA and profile fields."""

    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True)
    totp_secret = models.CharField(max_length=32, blank=True)
    totp_enabled = models.BooleanField(default=False)
    language = models.CharField(max_length=10, default="fr")
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    data_deletion_requested_at = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        ordering = ["email"]

    def __str__(self) -> str:
        return self.email
