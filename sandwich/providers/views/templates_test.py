from django.urls import reverse

from sandwich.core.factories.form import FormFactory


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
