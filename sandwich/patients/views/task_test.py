from http import HTTPStatus

import pytest
from django.test import Client
from django.urls import reverse
from guardian.shortcuts import remove_perm

from sandwich.core.factories.task import TaskFactory
from sandwich.core.models.patient import Patient
from sandwich.users.models import User


@pytest.mark.django_db
def test_patient_can_view_assigned_task_with_permission(
    patient: Patient,
    user: User,
) -> None:
    client = Client()
    # Ensure the patient's user is the one logging in
    client.force_login(user)
    task = TaskFactory.create(patient=patient)
    url = reverse("patients:task", kwargs={"patient_id": patient.id, "task_id": task.id})
    res = client.get(url)

    assert res.status_code == 200


@pytest.mark.django_db
def test_patient_denied_access_to_view_task_without_permission(
    patient: Patient,
    user: User,
) -> None:
    client = Client()
    # Ensure the patient's user is the one logging in
    client.force_login(user)
    task = TaskFactory.create(patient=patient)
    remove_perm("view_task", patient.user, task)
    url = reverse("patients:task", kwargs={"patient_id": patient.id, "task_id": task.id})
    res = client.get(url)

    assert res.status_code == 404


@pytest.mark.django_db
def test_task_view_includes_submit_url(client: Client, user: User, patient: Patient):
    """Request the patient task view and assert submit_url is provided."""

    task = TaskFactory.create(
        patient=patient,
        form_version=None,
    )

    client.force_login(user)

    url = reverse("patients:task", kwargs={"patient_id": patient.pk, "task_id": task.pk})
    response = client.get(url)

    # Ensure the view rendered and provided context
    assert response.status_code == HTTPStatus.OK
    assert "submit_url" in response.context

    submit_url = response.context["submit_url"]

    # We expect the URLs to end with the api paths for this task
    assert submit_url.endswith(f"/patients/api/form/{task.id}/submit")
