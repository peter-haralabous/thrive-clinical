import pytest
from django.test import Client
from django.urls import reverse

from sandwich.core.factories.invitation import InvitationFactory
from sandwich.core.factories.patient import PatientFactory
from sandwich.users.models import User


@pytest.mark.django_db
def test_accept_invite(user: User) -> None:
    patient = PatientFactory.create()
    invitation = InvitationFactory.create(patient=patient)
    client = Client()
    client.force_login(user)

    res = client.post(reverse("patients:accept_invite", kwargs={"token": invitation.token}), data={"accepted": True})

    assert res.status_code == 302
    assert res.url == reverse("patients:patient_details", kwargs={"patient_id": patient.id})  # type:ignore [attr-defined]
    patient.refresh_from_db()
    assert patient.user == user
    assert user.has_perm("change_patient", patient)
