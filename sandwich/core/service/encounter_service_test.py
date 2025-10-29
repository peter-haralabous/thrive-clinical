import pytest

from sandwich.core.models.encounter import Encounter
from sandwich.core.models.encounter import EncounterStatus
from sandwich.core.models.organization import Organization
from sandwich.core.models.patient import Patient
from sandwich.users.models import User


@pytest.mark.django_db
def test_assign_default_encounter_perms(
    provider: User, user: User, organization: Organization, patient: Patient
) -> None:
    encounter = Encounter.objects.create(
        organization=organization, patient=patient, status=EncounterStatus.IN_PROGRESS
    )

    assert user.has_perm("view_encounter", encounter)

    assert provider.has_perm("view_encounter", encounter)
    assert provider.has_perm("change_encounter", encounter)
