from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory

from sandwich.core.context_processors import patients_context
from sandwich.core.context_processors import settings_context
from sandwich.core.factories import PatientFactory
from sandwich.users.models import User


def test_settings_context():
    request = RequestFactory().get("/")
    context = settings_context(request)
    assert "environment" in context
    assert "app_version" in context


def test_patients_context_anonymous(rf: RequestFactory):
    request = rf.get("/")
    request.user = AnonymousUser()
    context = patients_context(request)
    assert context == {}


def test_patients_context_authenticated(user: User, rf: RequestFactory):
    patient1 = PatientFactory(user=user)
    patient2 = PatientFactory(user=user)
    request = rf.get("/")
    request.user = user
    context = patients_context(request)

    assert "user_patients" in context
    assert len(context["user_patients"]) == 2
    assert patient1 in context["user_patients"]
    assert patient2 in context["user_patients"]


def test_patients_context_authenticated_no_patients(user: User, rf: RequestFactory):
    request = rf.get("/")
    request.user = user
    context = patients_context(request)

    assert "user_patients" in context
    assert len(context["user_patients"]) == 0
