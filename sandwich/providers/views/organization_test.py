import pytest

from sandwich.providers.views.organization import OrganizationAdd


@pytest.mark.django_db
def test_organization_add_form() -> None:
    form_data = {
        "name": "Test Organization",
    }
    form = OrganizationAdd(data=form_data)
    assert form.is_valid(), f"Form errors: {form.errors}"
    organization = form.save()
    assert organization.name == "Test Organization"


minimal_form_data = {
    "name": "Test Organization",
    "patient_statuses": "[]",
    "verification_type": "DATE_OF_BIRTH",
}


@pytest.mark.django_db
def test_organization_add_form_no_statuses() -> None:
    form = OrganizationAdd(data=minimal_form_data)
    assert form.is_valid(), f"Form errors: {form.errors}"
    organization = form.save()
    assert organization.name == "Test Organization"
    assert len(organization.patient_statuses) == 0


@pytest.mark.django_db
def test_organization_with_same_name() -> None:
    org_a = OrganizationAdd(data=minimal_form_data).save()
    org_b = OrganizationAdd(data=minimal_form_data).save()
    assert org_a.pk != org_b.pk
    assert org_a.slug != org_b.slug
