import pytest
from django.test import Client
from django.urls import reverse

from sandwich.core.models.encounter import Encounter
from sandwich.core.models.encounter import EncounterStatus
from sandwich.core.models.organization import Organization
from sandwich.core.models.patient import Patient
from sandwich.core.models.task import Task
from sandwich.core.models.task import TaskStatus
from sandwich.core.service.task_service import assign_default_provider_task_perms
from sandwich.users.models import User


@pytest.mark.django_db
def test_task_view(
    provider: User,
    organization: Organization,
    patient: Patient,
) -> None:
    client = Client()
    client.force_login(provider)
    task = Task.objects.create(
        patient=patient,
        status=TaskStatus.IN_PROGRESS,
        encounter=Encounter.objects.create(
            organization=organization, patient=patient, status=EncounterStatus.IN_PROGRESS
        ),
    )
    assign_default_provider_task_perms(task)
    res = client.post(
        reverse(
            "providers:task", kwargs={"organization_id": organization.id, "patient_id": patient.id, "task_id": task.id}
        )
    )

    assert res.status_code == 200


@pytest.mark.django_db
def test_task_view_deny_access(
    provider: User,
    organization: Organization,
    patient: Patient,
) -> None:
    client = Client()
    client.force_login(provider)
    task = Task.objects.create(
        patient=patient,
        status=TaskStatus.IN_PROGRESS,
        encounter=Encounter.objects.create(
            organization=organization, patient=patient, status=EncounterStatus.IN_PROGRESS
        ),
    )
    res = client.post(
        reverse(
            "providers:task", kwargs={"organization_id": organization.id, "patient_id": patient.id, "task_id": task.id}
        )
    )

    assert res.status_code == 403
