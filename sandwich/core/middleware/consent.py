import logging
from collections.abc import Callable

from django.http import HttpRequest
from django.http import HttpResponse
from django.urls import reverse

from sandwich.core.models.consent import Consent
from sandwich.core.models.consent import ConsentPolicy
from sandwich.users.models import User


def _has_consented_to_policies(user: User, policies: set[str]) -> bool:
    consented_policies = {c.policy for c in Consent.objects.for_user(user) if c.decision is True}
    return policies.issubset(consented_policies)


def _handle_missing_consent(request: HttpRequest) -> None:
    # Placeholder for handling missing consent, e.g., redirect
    logging.info("%s has not consented to required policies, would redirect.", request.user)


class ConsentMiddleware:
    exempt_paths: set[str] = {
        reverse("core:healthcheck"),
    }

    required_policies: set[str] = {
        ConsentPolicy.THRIVE_PRIVACY_POLICY,
        ConsentPolicy.THRIVE_TERMS_OF_USE,
    }

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if (
            request.user
            and request.user.is_authenticated
            and not self.is_path_exempt(request.path)
            and not self.has_required_consents(request.user)
        ):
            _handle_missing_consent(request)  # will return
        return self.get_response(request)

    def is_path_exempt(self, path: str):
        """Some paths don't require policy consent"""
        return path in self.exempt_paths

    def has_required_consents(self, user: User):
        return _has_consented_to_policies(user, self.required_policies)
