from typing import Any

from sandwich.core.models.patient import Patient
from sandwich.core.util.http import AuthenticatedHttpRequest


def _patient_context(request: AuthenticatedHttpRequest, patient: Patient | None = None) -> dict[str, Any]:
    """Fetch additional template context required for patient context"""
    return {
        # used to show the right name in the top nav
        # and contextualizes all the links in the side nav
        "patient": patient
    }
