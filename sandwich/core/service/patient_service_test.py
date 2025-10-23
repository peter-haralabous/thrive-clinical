import pytest

from sandwich.core.factories.patient import PatientFactory
from sandwich.core.models.organization import Organization
from sandwich.users.models import User


@pytest.mark.django_db
def test_assign_default_provider_patient_permissions(user: User, provider: User, organization: Organization) -> None:
    # assign_default_provider_patient_permissions called in factory
    new_patient = PatientFactory.create(organization=organization)

    assert provider.has_perm("view_patient", new_patient)
    assert provider.has_perm("change_patient", new_patient)
    assert provider.has_perm("assign_task", new_patient)

    # random user doesn't have perms
    assert user.has_perm("view_patient", new_patient) is False
    assert user.has_perm("change_patient", new_patient) is False
    assert user.has_perm("assign_task", new_patient) is False
