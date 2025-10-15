# ruff: noqa: TC006

from typing import cast

import pytest
from guardian.shortcuts import assign_perm

from sandwich.core.factories import OrganizationFactory
from sandwich.core.models.organization import Organization
from sandwich.users.factories import UserFactory
from sandwich.users.models import User


@pytest.mark.django_db
def test_object_permissions_no_perms() -> None:
    user = cast(User, UserFactory())
    organization = cast(Organization, OrganizationFactory())

    assert user.has_perm("change_organization", organization) is False


@pytest.mark.django_db
def test_object_permissions_assign_perms() -> None:
    user = cast(User, UserFactory())
    organization = cast(Organization, OrganizationFactory())

    assign_perm("change_organization", user, organization)
    assert user.has_perm("change_organization", organization)

    # user only has permissions granted
    assert user.has_perm("delete_organization", organization) is False


@pytest.mark.django_db
def test_object_permissions_specific_to_object() -> None:
    user_a = cast(User, UserFactory())
    user_b = cast(User, UserFactory())
    organization_a = cast(Organization, OrganizationFactory())
    organization_b = cast(Organization, OrganizationFactory())

    # user_a is given permissions for org_a
    assign_perm("change_organization", user_a, organization_a)
    assert user_a.has_perm("change_organization", organization_a)

    assert user_a.has_perm("change_organization", organization_b) is False
    assert user_b.has_perm("change_organization", organization_a) is False
