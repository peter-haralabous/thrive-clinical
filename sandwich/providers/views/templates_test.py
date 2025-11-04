from django.urls import reverse
from guardian.shortcuts import remove_perm

from sandwich.core.factories.form import FormFactory
from sandwich.core.models.role import RoleName


def test_templates_home(client, provider, organization):
    client.force_login(provider)
    url = reverse("providers:templates_home", kwargs={"organization_id": organization.id})
    response = client.get(url)
    assert response.status_code == 200
    assert "provider/templates.html" in [t.name for t in response.templates]


def test_templates_home_user_not_in_organization_deny_access(client, user, organization):
    client.force_login(user)
    url = reverse("providers:templates_home", kwargs={"organization_id": organization.id})
    response = client.get(url)
    assert response.status_code == 404


def test_form_list(client, provider, organization):
    client.force_login(provider)
    url = reverse("providers:form_templates_list", kwargs={"organization_id": organization.id})
    response = client.get(url)
    assert response.status_code == 200
    assert "provider/form_list.html" in [t.name for t in response.templates]


def test_form_list_user_not_in_organization_deny_access(client, user, organization):
    client.force_login(user)
    url = reverse("providers:form_templates_list", kwargs={"organization_id": organization.id})
    response = client.get(url)
    assert response.status_code == 404


def test_form_list_filters_allowed_forms(client, provider, organization):
    """Only forms belonging to the organization are shown to a provider.

    And only forms that a provider has view_form permission for are shown.
    """
    # Add a form for another organization
    FormFactory.create(name="Org2 Form")

    # Add a couple for this provider's organization.
    form1 = FormFactory.create(organization=organization, name="Form 1")
    form2 = FormFactory.create(organization=organization, name="Form 2")

    client.force_login(provider)
    url = reverse("providers:form_templates_list", kwargs={"organization_id": organization.id})
    response = client.get(url)
    assert response.status_code == 200
    # The forms shown are only for the org the provider is in.
    assert response.context["forms"].object_list == [form1, form2]

    # Remove form2's view_form permission from the provider group to demonstrate that it would not be shown.
    provider_group = organization.get_role(RoleName.STAFF).group
    remove_perm("view_form", provider_group, form2)

    url = reverse("providers:form_templates_list", kwargs={"organization_id": organization.id})
    response = client.get(url)
    # Only form1 is shown now.
    assert response.context["forms"].object_list == [form1]


def test_form_details(client, provider, organization):
    form = FormFactory.create(organization=organization)
    client.force_login(provider)
    url = reverse("providers:form_template", kwargs={"organization_id": organization.id, "form_id": form.id})
    response = client.get(url)
    assert response.status_code == 200
    assert "provider/form_details.html" in [t.name for t in response.templates]


def test_form_details_user_not_in_organization_deny_access(client, user, organization):
    form = FormFactory.create(organization=organization)
    client.force_login(user)
    url = reverse("providers:form_template", kwargs={"organization_id": organization.id, "form_id": form.id})
    response = client.get(url)
    assert response.status_code == 404


def test_form_details_patient_deny_access(client, patient, organization):
    """Patient in org cannot access provider's view of a form template."""
    form = FormFactory.create(organization=organization)
    client.force_login(patient.user)
    url = reverse("providers:form_template", kwargs={"organization_id": organization.id, "form_id": form.id})
    response = client.get(url)
    assert response.status_code == 404
