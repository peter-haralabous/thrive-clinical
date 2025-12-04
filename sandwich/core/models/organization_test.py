from unittest.mock import patch

import pytest

from sandwich.core.models import Organization
from sandwich.core.models import OrganizationVerification
from sandwich.users.models import User


@pytest.mark.django_db
def test_organization_create_assigns_permissions() -> None:
    # test for create_default_roles_and_perms can be found in
    # sandwich/core/service/organization_service_test.py
    with patch("sandwich.core.service.organization_service.create_default_roles_and_perms") as mock_create:
        created = Organization.objects.create(name="test org", slug="is_this_unique")
        mock_create.assert_called_once_with(created)


@pytest.mark.django_db
def test_new_organization_is_unverified() -> None:
    new_org = Organization.objects.create(name="test org", slug="is_this_unique")
    assert new_org.verified is False


@pytest.mark.django_db
def test_organization_can_be_verified() -> None:
    new_org = Organization.objects.create(name="test org", slug="is_this_unique")
    staff_user = User.objects.create(is_staff=True)

    assert new_org.verified is False
    OrganizationVerification.objects.create(organization=new_org, approver=staff_user)
    assert new_org.verified is True
