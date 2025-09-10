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


class OrganizationEdit(forms.ModelForm[Organization]):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", "Submit"))

    class Meta:
        model = Organization
        fields = ("name",)


class OrganizationAdd(forms.ModelForm[Organization]):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", "Submit"))

    class Meta:
        model = Organization
        fields = ("name",)


@login_required
def organization_edit(request: HttpRequest, organization_id: int) -> HttpResponse:
    organization = get_object_or_404(Organization, id=organization_id)

    if request.method == "POST":
        form = OrganizationEdit(request.POST, instance=organization)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, "Organization updated successfully.")
            return HttpResponseRedirect(reverse("providers:organization", kwargs={"organization_id": organization_id}))
    else:
        form = OrganizationEdit(instance=organization)

    context = {"form": form}
    return render(request, "provider/organization_edit.html", context)


@login_required
def organization_add(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = OrganizationAdd(request.POST)
        if form.is_valid():
            organization = form.save()
            messages.add_message(request, messages.SUCCESS, "Organization added successfully.")
            return HttpResponseRedirect(reverse("providers:organization", kwargs={"organization_id": organization.id}))
    else:
        form = OrganizationAdd()

    context = {"form": form}
    return render(request, "provider/organization_add.html", context)
