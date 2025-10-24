from datetime import date
from http import HTTPStatus
from typing import Any

import pytest
from django.test import Client
from django.urls import reverse

from sandwich.core.factories.patient import PatientFactory
from sandwich.core.models import Fact
from sandwich.core.models.patient import Patient
from sandwich.patients.views.patient import PatientAdd
from sandwich.patients.views.patient import PatientEdit
from sandwich.users.models import User


@pytest.mark.django_db
def test_patient_edit_post_updates_patient(db, patient: Patient, user: User) -> None:
    client = Client()
    client.force_login(user)
    url = reverse("patients:patient_edit", kwargs={"patient_id": patient.pk})
    data = {
        "first_name": "New",
        "last_name": patient.last_name,
        "date_of_birth": patient.date_of_birth,
        "province": "BC",
        "phn": "9111111117",  # BC requires more specific PHN
    }
    response = client.post(url, data)
    assert response.status_code == HTTPStatus.FOUND
    assert response.headers.get("Location") == reverse("patients:patient_edit", kwargs={"patient_id": patient.id})
    patient.refresh_from_db()
    assert patient.first_name == "New"


@pytest.mark.django_db
# NB: patient fixture required, user needs a patient to bypass profile creation
def test_patient_add(db, user: User, patient: Patient) -> None:
    client = Client()
    client.force_login(user)
    url = reverse("patients:patient_add")
    data = {
        "first_name": "Jacob",
        "last_name": "Newpatient",
        "date_of_birth": date(1961, 6, 6),
        "province": "BC",
        "phn": "9111111117",  # BC requires more specific PHN
    }
    response = client.post(url, data)
    created_patient = Patient.objects.get(last_name="Newpatient")
    assert created_patient
    assert response.status_code == HTTPStatus.FOUND
    assert response.headers.get("Location") == reverse(
        "patients:patient_details", kwargs={"patient_id": created_patient.id}
    )
    assert user.has_perm("change_patient", created_patient)


@pytest.mark.django_db
def test_patient_onboarding_add(db, user: User) -> None:
    client = Client()
    client.force_login(user)
    url = reverse("patients:patient_onboarding_add")
    data = {
        "first_name": "Jacob",
        "last_name": "Newpatient",
        "date_of_birth": date(1961, 6, 6),
        "province": "BC",
        "phn": "9111111117",  # BC requires more specific PHN
    }
    response = client.post(url, data)
    created_patient = Patient.objects.get(last_name="Newpatient")
    assert created_patient
    assert response.status_code == HTTPStatus.FOUND
    assert response.headers.get("Location") == reverse("patients:home")
    assert user.has_perm("change_patient", created_patient)


@pytest.mark.django_db
def test_patient_details(user: User, patient: Patient) -> None:
    client = Client()
    client.force_login(user)
    res = client.get(
        reverse(
            "patients:patient_details",
            kwargs={
                "patient_id": patient.id,
            },
        )
    )

    assert res.status_code == 200


@pytest.mark.django_db
# NB: patient fixture required
def test_patient_details_deny_access(user: User, patient: Patient) -> None:
    other_patient = PatientFactory.create()
    client = Client()
    client.force_login(user)
    res = client.get(
        reverse(
            "patients:patient_details",
            kwargs={
                "patient_id": other_patient.id,
            },
        )
    )

    assert res.status_code == 404


@pytest.mark.parametrize(
    ("data", "is_valid"),
    [
        pytest.param(
            {
                "first_name": "Tad",
                "last_name": "Cooper",
                "date_of_birth": "1961-11-11",
            },
            True,
            id="Pass: All required fields present, date in past.",
        ),
        pytest.param(
            {
                "first_name": "Tad",
                "last_name": "Cooper",
                "date_of_birth": "2500-11-11",
            },
            False,
            id="Fail: date of birth in future",
        ),
        pytest.param(
            {
                "last_name": "Cooper",
                "date_of_birth": "1961-11-11",
            },
            False,
            id="Fail: missing required field",
        ),
        pytest.param(
            {
                "first_name": "Tad",
                "last_name": "Cooper",
                "date_of_birth": "1961-11-11",
                "province": "BC",
                "phn": "9111111117",
            },
            True,
            id="Pass: BC phn is valid",
        ),
        pytest.param(
            {
                "first_name": "Tad",
                "last_name": "Cooper",
                "date_of_birth": "1961-11-11",
                "province": "BC",
                "phn": "9111111119",
            },
            False,
            id="Fail: BC phn is not valid",
        ),
    ],
)
def test_patient_edit_form(data: dict[str, Any], *, is_valid: bool) -> None:
    patient_form = PatientEdit(data)
    assert patient_form.is_valid() == is_valid


@pytest.mark.parametrize(
    ("data", "is_valid"),
    [
        pytest.param(
            {
                "first_name": "Tad",
                "last_name": "Cooper",
                "date_of_birth": "1961-11-11",
            },
            True,
            id="Pass: All required fields present, date in past.",
        ),
        pytest.param(
            {
                "first_name": "Tad",
                "last_name": "Cooper",
                "date_of_birth": "2500-11-11",
            },
            False,
            id="Fail: date of birth in future",
        ),
        pytest.param(
            {
                "last_name": "Cooper",
                "date_of_birth": "1961-11-11",
            },
            False,
            id="Fail: missing required field",
        ),
        pytest.param(
            {
                "first_name": "Tad",
                "last_name": "Cooper",
                "date_of_birth": "1961-11-11",
                "province": "BC",
                "phn": "9111111117",
            },
            True,
            id="Pass: BC phn is valid",
        ),
        pytest.param(
            {
                "first_name": "Tad",
                "last_name": "Cooper",
                "date_of_birth": "1961-11-11",
                "province": "BC",
                "phn": "9111111119",
            },
            False,
            id="Fail: BC phn is not valid",
        ),
    ],
)
def test_patient_create_form(data: dict[str, Any], *, is_valid: bool) -> None:
    patient_form = PatientAdd(data)
    assert patient_form.is_valid() == is_valid


def test_patient_details_kg(
    db, client: Client, user: User, patient: Patient, patient_knowledge_graph: list[Fact]
) -> None:
    client.force_login(user)
    url = reverse("patients:patient_details", kwargs={"patient_id": patient.pk})
    response = client.get(url)

    facts = response.context["facts"]

    category_length = {
        "allergies": 1,
        "conditions": 2,
        "documents_and_notes": 1,
        "family_history": 0,
        "hospital_visits": 0,
        "immunizations": 1,
        "injuries": 0,
        "lab_results": 0,
        "medications": 1,
        "practitioners": 0,
        "procedures": 1,
        "symptoms": 1,
    }
    all_categories = set(category_length.keys())
    assert set(facts.keys()) == all_categories, "Fact categories do not match expected categories."

    for category, length in category_length.items():
        assert len(facts[category]) == length, (
            f"Expected {length} facts in category '{category}', found {len(facts[category])}."
        )
