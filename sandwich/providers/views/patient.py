from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.http import HttpResponse
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse

from sandwich.core.models import Organization
from sandwich.core.models import Patient


class PatientEdit(forms.ModelForm[Patient]):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", "Submit"))

    class Meta:
        model = Patient
        fields = ("first_name", "last_name", "email", "phn", "date_of_birth")
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
        }


class PatientAdd(forms.ModelForm[Patient]):
    # TODO: add check for duplicate patient
    #       "you already have a patient with this email address/PHN/name"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", "Submit"))

    def save(self, commit=True, organization: Organization | None = None):  # noqa: FBT002
        instance = super().save(commit=False)
        if organization is not None:
            instance.organization = organization
        if commit:
            instance.save()
        return instance

    class Meta:
        model = Patient
        fields = ("first_name", "last_name", "email", "phn", "date_of_birth")
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
        }


@login_required
def patient_edit(request: HttpRequest, patient_id: int, organization_id: int | None = None) -> HttpResponse:
    patient = get_object_or_404(Patient, id=patient_id)

    # make sure that the organization id in the route matches the organization id of the patient
    # a tricksy user might have edited the URL manually
    assert patient.organization_id is not None, "Patient has no organization"
    if patient.organization_id != organization_id:
        return HttpResponseRedirect(
            reverse(
                "providers:organization_patient",
                kwargs={"patient_id": patient.id, "organization_id": patient.organization_id},
            )
        )

    if request.method == "POST":
        form = PatientEdit(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, "Patient updated successfully.")
            return HttpResponseRedirect(
                reverse(
                    "providers:organization_patient",
                    kwargs={"patient_id": patient.id, "organization_id": patient.organization_id},
                )
            )
    else:
        form = PatientEdit(instance=patient)

    context = {"form": form}
    return render(request, "provider/patient_edit.html", context)


@login_required
def patient_add(request: HttpRequest, organization_id: int) -> HttpResponse:
    organization = get_object_or_404(Organization, id=organization_id)
    if request.method == "POST":
        form = PatientAdd(request.POST)
        if form.is_valid():
            patient = form.save(organization=organization)
            messages.add_message(request, messages.SUCCESS, "Patient added successfully.")
            return HttpResponseRedirect(reverse("providers:patient", kwargs={"patient_id": patient.id}))
    else:
        form = PatientAdd()

    context = {"form": form}
    return render(request, "provider/patient_add.html", context)


@login_required
def organization_patient_list(request: HttpRequest, organization_id: int) -> HttpResponse:
    organization = get_object_or_404(Organization, id=organization_id)
    patients = list(Patient.objects.filter(organization=organization))
    return render(request, "provider/patient_list.html", {"patients": patients, "organization": organization})
