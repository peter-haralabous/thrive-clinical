from anymail.signals import EventType
from django.db import models

from sandwich.core.models.abstract import BaseModel


class EmailType(models.TextChoices):
    invitation = "invitation", "Invitation"
    task = "task", "Task"


class EmailStatus(models.TextChoices):
    AUTORESPONDED = EventType.AUTORESPONDED, "Autoresponded"
    BOUNCED = EventType.BOUNCED, "Bounced"
    CLICKED = EventType.CLICKED, "Clicked"
    COMPLAINED = EventType.COMPLAINED, "Complained"
    DEFERRED = EventType.DEFERRED, "Deferred"
    DELIVERED = EventType.DELIVERED, "Delivered"
    FAILED = EventType.FAILED, "Failed"
    INBOUND = EventType.INBOUND, "Inbound"
    INBOUND_FAILED = EventType.INBOUND_FAILED, "Inbound Failed"
    OPENED = EventType.OPENED, "Opened"
    QUEUED = EventType.QUEUED, "Queued"
    REJECTED = EventType.REJECTED, "Rejected"
    SENT = EventType.SENT, "Sent"
    SUBSCRIBED = EventType.SUBSCRIBED, "Subscribed"
    UNKNOWN = EventType.UNKNOWN, "Unknown"
    UNSUBSCRIBED = EventType.UNSUBSCRIBED, "Unsubscribed"


class Email(BaseModel):
    to = models.TextField()
    type = models.TextField(choices=EmailType)
    status = models.CharField(max_length=50, choices=EmailStatus, blank=True, default="")
    message_id = models.TextField(blank=True, default="")  # from ses
    invitation = models.ForeignKey("Invitation", on_delete=models.CASCADE, null=True)
