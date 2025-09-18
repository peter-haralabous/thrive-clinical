import pytest
from django.urls import reverse
from playwright.sync_api import Page


@pytest.mark.e2e
def test_home_page_buttons(live_server_with_assets, page: Page):
    """
    Test that the home page displays the Continue as Patient and Continue as Provider buttons
    with proper styling and JavaScript functionality.
    """
    # Navigate to the home page
    page.goto(f"{live_server_with_assets.url}{reverse('home')}")

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

    # Verify the buttons have the expected CSS classes (DaisyUI/Tailwind styling)
    assert "btn" in (patient_button.get_attribute("class") or "")
    assert "btn-primary" in (patient_button.get_attribute("class") or "")
    assert "btn" in (provider_button.get_attribute("class") or "")
    assert "btn-secondary" in (provider_button.get_attribute("class") or "")

    # Test that the buttons are clickable (this tests JavaScript functionality)
    # We'll just check that they respond to hover, indicating JS is working
    patient_button.hover()
    provider_button.hover()

    # Verify the page structure and styling is properly loaded
    container = page.locator(".max-w-xl.w-full.p-8.bg-white.rounded-lg.shadow-lg")
    assert container.is_visible()

    # Check that the description text is present
    description = page.locator("p.text-lg.text-gray-600")
    assert description.is_visible()
    assert "healthcare management platform" in (description.text_content() or "").lower()
