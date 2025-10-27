import logging

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render

from sandwich.core.models import Patient
from sandwich.core.service.permissions_service import ObjPerm
from sandwich.core.service.permissions_service import authorize_objects
from sandwich.core.util.http import AuthenticatedHttpRequest
from sandwich.patients.service.fact_service import categorized_facts_for_patient
from sandwich.patients.views.patient import _patient_context

logger = logging.getLogger(__name__)


@login_required
@authorize_objects([ObjPerm(Patient, "patient_id", ["view_patient"])])
def patient_details(request: AuthenticatedHttpRequest, patient: Patient) -> HttpResponse:
    # TODO-NG: page & sort these lists
    tasks = patient.task_set.all()
    documents = patient.document_set.all()

    context = {
        "patient": patient,
        "tasks": tasks,
        "documents": documents,
        "facts": categorized_facts_for_patient(patient),
    } | _patient_context(request, patient=patient)
    return render(request, "patient/patient_details.html", context)
