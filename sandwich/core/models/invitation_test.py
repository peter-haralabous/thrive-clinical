import pytest
from guardian.shortcuts import get_group_perms
from guardian.shortcuts import get_perms

from sandwich.core.models.invitation import Invitation
from sandwich.core.models.invitation import InvitationStatus
from sandwich.core.models.patient import Patient
from sandwich.core.models.role import RoleName


@pytest.mark.django_db
def test_invitation_creation_assigns_permissions(patient: Patient) -> None:
    created = Invitation.objects.create(status=InvitationStatus.PENDING, token="", patient=patient)

    user_permissions = get_perms(patient.user, created)

    assert "view_invitation" in user_permissions
    assert "change_invitation" in user_permissions

    assert patient.organization is not None
    for role in [RoleName.OWNER, RoleName.ADMIN, RoleName.STAFF]:
        group = patient.organization.get_role(role).group
        group_permissions = get_group_perms(group, created)
        assert group_permissions.filter(codename="view_invitation").exists()
        assert group_permissions.filter(codename="change_invitation").exists()
