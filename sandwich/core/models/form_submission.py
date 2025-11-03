from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_enum import EnumField

from sandwich.core.models.abstract import BaseModel
from sandwich.core.models.form import Form
from sandwich.core.models.patient import Patient
from sandwich.core.models.task import Task


class FormSubmissionStatus(models.TextChoices):
    DRAFT = "draft", _("Draft")
    COMPLETED = "completed", _("Completed")


class FormSubmission(BaseModel):
    """
    Stores a patient's data for a specific form, linking it to an assigned task.
    """

    form = models.ForeignKey(
        Form, on_delete=models.SET_NULL, null=True, help_text="The original form this submission is for"
    )
    task = models.OneToOneField(
        Task, on_delete=models.SET_NULL, null=True, blank=True, help_text="The specific task this submission is for"
    )
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, help_text="The patient this form submission is for")
    status: models.Field[FormSubmissionStatus, FormSubmissionStatus] = EnumField(
        FormSubmissionStatus, help_text="current state of submission"
    )
    form_version = models.ForeignKey(
        "core.FormEvent",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        help_text="The specific version of the form this submission uses",
    )
    data = models.JSONField(default=dict)
    metadata = models.JSONField(default=dict)

    submitted_at = models.DateTimeField(null=True)

    def submit(self):
        if self.status == FormSubmissionStatus.DRAFT:
            self.status = FormSubmissionStatus.COMPLETED
            self.submitted_at = timezone.now()
            self.save()
