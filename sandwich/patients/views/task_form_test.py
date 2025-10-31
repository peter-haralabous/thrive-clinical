import pytest
from django.urls import reverse
from playwright.sync_api import Page

from sandwich.core.factories.form import FormFactory
from sandwich.core.factories.task import TaskFactory
from sandwich.core.models.patient import Patient


@pytest.mark.e2e
def test_task_form_component_renders(live_server, page: Page, patient: Patient, auth_cookies: None):
    """Validate patient task form load and assert the SurveyForm renders properly."""
    schema = {"elements": [{"type": "text", "name": "yourName", "title": "What is your name?"}]}
    form = FormFactory.create(name="E2E Test Form", schema=schema, organization=patient.organization)
    task = TaskFactory.create(patient=patient, form_version=form.events.last())

    task_url_path = reverse("patients:task", kwargs={"patient_id": patient.id, "task_id": task.id})
    url = f"{live_server.url}{task_url_path}"

    # Navigate to the task page and wait for the important selectors below.
    page.goto(url)
    page.wait_for_selector("survey-form", state="attached", timeout=5000)

    script_sel = "#form_schema[type='application/json']"
    page.wait_for_selector(script_sel, state="attached", timeout=5000)
    script_el = page.query_selector(script_sel)
    assert script_el is not None
    text = script_el.text_content()
    assert "yourName" in (text or "")

    page.wait_for_selector("survey-form [data-survey-container][data-survey-rendered]", timeout=5000)

    input_by_label = page.get_by_label("What is your name?")
    assert input_by_label is not None
    # ensure the element exists and is visible
    assert input_by_label.count() > 0, "Expected an input labelled 'What is your name?' to be present"
    assert input_by_label.first.is_visible(), "Expected the 'yourName' input to be visible"
