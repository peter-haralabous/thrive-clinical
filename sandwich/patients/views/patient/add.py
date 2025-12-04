import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from sandwich.core.util.http import AuthenticatedHttpRequest
from sandwich.patients.forms.patient_add import PatientAdd
from sandwich.patients.views.patient import _patient_context

logger = logging.getLogger(__name__)


@login_required
def patient_add(request: AuthenticatedHttpRequest) -> HttpResponse:
    logger.info("Accessing patient add", extra={"user_id": request.user.id})

    if request.method == "POST":
        logger.info("Processing patient add form", extra={"user_id": request.user.id})
        form = PatientAdd(request.POST)
        if form.is_valid():
            patient = form.save(user=request.user)
            patient.assign_user_owner_perms(request.user)
            logger.info("Patient created successfully", extra={"user_id": request.user.id, "patient_id": patient.id})
            messages.add_message(request, messages.SUCCESS, "Patient added successfully.")
            return HttpResponseRedirect(reverse("patients:patient_details", kwargs={"patient_id": patient.id}))
        logger.warning(
            "Invalid patient add form", extra={"user_id": request.user.id, "form_errors": list(form.errors.keys())}
        )
    else:
        logger.debug("Rendering patient add form", extra={"user_id": request.user.id})
        form = PatientAdd()

    context = {"form": form} | _patient_context(request)
    return render(request, "patient/patient_add.html", context)


@login_required
def patient_onboarding_add(request: AuthenticatedHttpRequest) -> HttpResponse:
    logger.info("Accessing patient add", extra={"user_id": request.user.id})

    if request.user.patient_set.exists():
        logger.info("User already has a patient, redirecting to home", extra={"user_id": request.user.id})
        return HttpResponseRedirect(reverse("patients:home"))

    if request.method == "POST":
        logger.info("Processing patient add form", extra={"user_id": request.user.id})
        form = PatientAdd(request.POST)
        if form.is_valid():
            patient = form.save(user=request.user)
            patient.assign_user_owner_perms(request.user)
            logger.info("Patient created successfully", extra={"user_id": request.user.id, "patient_id": patient.id})
            messages.add_message(request, messages.SUCCESS, "Patient added successfully.")
            return HttpResponseRedirect(reverse("patients:home"))
        logger.warning(
            "Invalid patient add form", extra={"user_id": request.user.id, "form_errors": list(form.errors.keys())}
        )
    else:
        logger.debug("Rendering patient add form", extra={"user_id": request.user.id})
        form = PatientAdd()

    context = {"form": form} | _patient_context(request)
    return render(request, "patient/patient_onboarding_add.html", context)
