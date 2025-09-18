from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone

from sandwich.core.models.task import Task
from sandwich.core.models.task import TaskStatus
from sandwich.core.service.email_service import send_email
from sandwich.core.service.invitation_service import find_or_create_patient_invitation

# FIXME-NG: move to settings.py
APP_URL = "http://localhost:3000"


def cancel_task(task: Task) -> None:
    """Cancel a pending task."""
    assert task.active, "Task is not active"
    task.status = TaskStatus.CANCELLED
    task.ended_at = timezone.now()
    task.save()


def complete_task(task: Task) -> None:
    """Complete a task."""
    assert task.active, "Task is not active"
    task.status = TaskStatus.COMPLETED
    task.ended_at = timezone.now()
    task.save()


def send_task_added_email(task: Task) -> None:
    to = task.patient.email
    subject = "You've been assigned a task!"
    if task.patient.user:
        # they've already signed up; just send them to their tasks page
        task_url = APP_URL + reverse("patients:patient_details", kwargs={"patient_id": task.patient.id})
    else:
        # otherwise we need to send them an invitation link
        invitation = find_or_create_patient_invitation(task.patient)
        task_url = APP_URL + reverse("patients:accept_invite", kwargs={"token": invitation.token})

    body = render_to_string("email/task_added_body.txt", {"task": task, "task_url": task_url})
    send_email(to, subject, body)
