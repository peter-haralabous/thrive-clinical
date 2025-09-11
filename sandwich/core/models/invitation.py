from datetime import datetime
from datetime import timedelta
from uuid import uuid4

from django.db import models
from django.utils import timezone

from sandwich.core.models.abstract import TimestampedModel


class InvitationStatus(models.TextChoices):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"
    EXPIRED = "EXPIRED"
    FAILED_VERIFICATION = "FAILED_VERIFICATION"


INVITE_EXPIRY_DAYS = 90


def default_expiry() -> datetime:
    return timezone.now() + timedelta(days=INVITE_EXPIRY_DAYS)


class Invitation(TimestampedModel):
    status = models.CharField(
        choices=InvitationStatus,
        default=InvitationStatus.PENDING,
    )
    # The token isn't visible to the sender, only to the receiver
    token = models.UUIDField(default=uuid4, editable=False, unique=True)

    expires_at = models.DateTimeField(default=default_expiry, null=True)
    accepted_at = models.DateTimeField(null=True)
    last_invited_at = models.DateTimeField(default=timezone.now)

    patient = models.ForeignKey("Patient", on_delete=models.CASCADE)
