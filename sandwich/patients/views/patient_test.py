from http import HTTPStatus

from django.test import Client
from django.urls import reverse

from sandwich.core.factories import PatientFactory
from sandwich.users.models import User


def test_patient_edit_post_updates_patient(db, user: User) -> None:
    patient = PatientFactory.create(user=user, first_name="Old")
    client = Client()
    client.force_login(user)
    url = reverse("patients:patient_edit", kwargs={"patient_id": patient.pk})
    data = {
        "first_name": "New",
        "last_name": patient.last_name,
        "email": patient.email,
        "phn": patient.phn,
        "date_of_birth": patient.date_of_birth,
    }
    response = client.post(url, data)
    assert response.status_code == HTTPStatus.FOUND
    patient.refresh_from_db()
    assert patient.first_name == "New"
