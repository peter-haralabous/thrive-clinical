import re

import pytest

from sandwich.core.models import Invitation
from sandwich.core.models import Patient
from sandwich.core.models.invitation import InvitationStatus
from sandwich.core.service.invitation_service import get_unaccepted_invitation
from sandwich.core.service.invitation_service import resend_patient_invitation_email

UUID_PATTERN = re.compile("[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}|[0-9a-zA-Z_-]{43}")


def mask_uuids(s: str) -> str:
    """hide UUIDs and token_urlsafe strings, for snapshot testing"""

    def replacement(match: re.Match) -> str:
        match len(match.group(0)):
            case 36:
                return "xxxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
            case x:
                return "x" * x

    return UUID_PATTERN.sub(replacement, s)


def test_mask_uuids():
    assert mask_uuids("hello world") == "hello world"
    assert (
        mask_uuids("foo 75ab8e12-a6bf-4012-950b-35f174d987d1 bar f4135bac-b42d-4109-a503-1a4aea3da2a0")
        == "foo xxxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx bar xxxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    )
    assert (
        mask_uuids("click here: http://example.com/RmCLYiNa9BGGAGzpg1dKnqNNS2hUO4zTL3xSmO_fJIw/")
        == "click here: http://example.com/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx/"
    )


@pytest.mark.django_db
def test_resend_patient_invitation_email(template_fixture: None, patient: Patient, mailoutbox, snapshot):
    resend_patient_invitation_email(patient)
    assert len(mailoutbox) == 1
    assert mailoutbox[0].to == [patient.email]

    # if the template changes, the snapshot will need to be updated
    assert mask_uuids(mailoutbox[0].body) == snapshot


@pytest.mark.django_db
def test_get_unaccepted_invitation_returns_non_accepted_invites() -> None:
    patient = Patient.objects.create(
        email="test@example.com", first_name="Test", last_name="Patient", date_of_birth="1990-01-01"
    )

    expected = Invitation.objects.create(patient=patient)
    actual = get_unaccepted_invitation(patient)
    assert actual is not None
    assert expected.id == actual.id


@pytest.mark.django_db
def test_get_unaccepted_invitation_ignores_accepted() -> None:
    patient = Patient.objects.create(
        email="test@example.com", first_name="Test", last_name="Patient", date_of_birth="1990-01-01"
    )

    Invitation.objects.create(patient=patient, status=InvitationStatus.ACCEPTED)
    actual = get_unaccepted_invitation(patient)
    assert actual is None
