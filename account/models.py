import uuid

from django.conf import settings
from django.contrib.auth.models import User as DjangoUser
from django.db import models
from django.utils import timezone


# Create your models here.

class MultiDomainAuthRequest(models.Model):
    class Status(models.TextChoices):
        CREATED = 'CREATED', 'Created on alt domain'
        RECEIVED = 'RECEIVED', 'Received by main domain'
        CONFIRMED = 'CONFIRMED', 'Login confirmed by main domain'
        DENIED = 'DENIED', 'Login denied by main domain'
        COMPLETED = 'COMPLETED', 'Login completed on alt domain'

    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='multidomain_auth_requests'
    )

    nonce = models.CharField(
        max_length=64,
        null=False,
        blank=False,
        help_text="Nonce to bind to session for security."
    )

    callback_uri = models.URLField(
        max_length=500,
        help_text="Callback URI to redirect back to alt domain after login."
    )

    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.CREATED,
    )

    timestamp_created = models.DateTimeField(auto_now_add=True,
                                             help_text="Timestamp when the request was created on the alt domain.")
    timestamp_received = models.DateTimeField(null=True, blank=True,
                                              help_text="Timestamp when the request was received by the main domain.")
    timestamp_answered = models.DateTimeField(null=True, blank=True,
                                              help_text="Timestamp when the request was confirmed/denied on the main domain.")
    timestamp_completed = models.DateTimeField(null=True, blank=True,
                                               help_text="Timestamp when the login was completed on the alt domain.")

    def is_recently_created(self, max_age_seconds: int = 120) -> bool:
        if self.status != self.Status.CREATED or self.timestamp_created is None:
            return False
        return (timezone.now() - self.timestamp_created).total_seconds() <= max_age_seconds

    def is_recently_confirmed(self, max_age_seconds: int = 120) -> bool:
        if self.status != self.Status.CONFIRMED or self.timestamp_answered is None:
            return False
        return (timezone.now() - self.timestamp_answered).total_seconds() <= max_age_seconds

    def __str__(self):
        return f"ExtAuthRequest(uid={self.uid}, status={self.status}, user={self.user})"


# Proxy models

class User(DjangoUser):
    class Meta(DjangoUser.Meta):
        proxy = True
