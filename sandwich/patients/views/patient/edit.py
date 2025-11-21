import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from sandwich.core.models import Patient
from sandwich.core.service.permissions_service import ObjPerm
from sandwich.core.service.permissions_service import authorize_objects
from sandwich.core.util.http import AuthenticatedHttpRequest
from sandwich.core.validators.phn import phn_attr_for_province
from sandwich.patients.forms.patient_edit import PatientEdit
from sandwich.patients.views.patient import _patient_context

logger = logging.getLogger(__name__)


@login_required
@authorize_objects([ObjPerm(Patient, "patient_id", ["view_patient", "change_patient"])])
def patient_edit(request: AuthenticatedHttpRequest, patient: Patient) -> HttpResponse:
    logger.info("Accessing patient edit", extra={"user_id": request.user.id, "patient_id": patient.id})

    if request.method == "POST":
        logger.info("Processing patient edit form", extra={"user_id": request.user.id, "patient_id": patient.id})
        form = PatientEdit(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            logger.info("Patient updated successfully", extra={"user_id": request.user.id, "patient_id": patient.id})
            messages.add_message(request, messages.SUCCESS, "Patient updated successfully.")
            return HttpResponseRedirect(reverse("patients:patient_edit", kwargs={"patient_id": patient.id}))
        logger.warning(
            "Invalid patient edit form",
            extra={"user_id": request.user.id, "patient_id": patient.id, "form_errors": list(form.errors.keys())},
        )
    else:
        logger.debug("Rendering patient edit form", extra={"user_id": request.user.id, "patient_id": patient.id})
        form = PatientEdit(instance=patient)

    context = {"form": form} | _patient_context(request, patient=patient)
    return render(request, "patient/patient_edit.html", context)


@login_required
def get_phn_validation(request: AuthenticatedHttpRequest) -> HttpResponse:
    province = request.GET.get("province")

    # Note: being used for patient add/onbboarding, might have to change
    form = PatientEdit()

    attrs = phn_attr_for_province(province)

    # Update the attributes on the form
    form.fields["phn"].widget.attrs.update(attrs)

    logger.debug(
        "Phn pattern results",
        extra={"user_id": request.user.id, "attrs": form.fields["phn"].widget.attrs},
    )

    return render(request, "patient/partials/phn_input.html", {"form": form})
