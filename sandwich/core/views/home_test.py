import pytest
from django.urls import reverse
from playwright.sync_api import Page


@pytest.mark.e2e
def test_home_page_buttons(live_server, page: Page):
    """
    Test that the home page displays the Continue as Patient and Continue as Provider buttons
    """
    # Navigate to the home page
    page.goto(f"{live_server.url}{reverse('home')}")

    # Wait for the page to load completely
    page.wait_for_load_state("networkidle")

    # Check that the main heading is present
    heading = page.locator("h1")
    assert heading.is_visible()
    assert "HealthConnect" in (heading.text_content() or "")

    # Check that the Continue as Patient button is present and visible
    patient_button = page.get_by_text("Continue as Patient")
    assert patient_button.is_visible()

    # Check that the Continue as Provider button is present and visible
    provider_button = page.get_by_text("Continue as Provider")
    assert provider_button.is_visible()
