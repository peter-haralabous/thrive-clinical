import pytest
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.test import RequestFactory
from django.urls import reverse

from sandwich.patients.middleware.patient_access import PatientAccessMiddleware
from sandwich.users.models import User


@pytest.mark.django_db
def test_patient_access_middleware(user: User, rf: RequestFactory):
    """
    GIVEN a user without a patient
    WHEN they try to access a page that is not on the allowed list
    THEN they should be redirected to the add patient page
    """
    request = rf.get(reverse("patients:home"))
    request.user = user
    middleware = PatientAccessMiddleware(lambda req: HttpResponse("OK"))
    response = middleware(request)
    assert isinstance(response, HttpResponseRedirect)
    assert response.url == reverse("patients:patient_add")


@pytest.mark.django_db
def test_patient_access_middleware_allowed_route(user: User, rf: RequestFactory):
    """
    GIVEN a user without a patient
    WHEN they try to access a page that is on the allowed list
    THEN they should be allowed to access the page
    """
    request = rf.get(reverse("patients:patient_add"))
    request.user = user
    middleware = PatientAccessMiddleware(lambda req: HttpResponse("OK"))
    response = middleware(request)
    assert response.status_code == 200
