from django.conf import settings

from sandwich.core.util.http import AuthenticatedHttpRequest


def settings_context(request):
    """Returns context variables from settings."""
    return {
        "environment": getattr(settings, "ENVIRONMENT", None),
        "app_version": getattr(settings, "APP_VERSION", None),
    }


def patients_context(request: AuthenticatedHttpRequest):
    """Attaches all patients for the current user."""
    patients = request.user.patient_set.all()
    return {
        "user_patients": list(patients),
    }
