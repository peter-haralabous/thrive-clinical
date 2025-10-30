import logging
from uuid import UUID

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse

from sandwich.core.models.custom_attribute import CustomAttribute
from sandwich.core.models.encounter import Encounter
from sandwich.core.models.organization import Organization
from sandwich.core.service.permissions_service import ObjPerm
from sandwich.core.service.permissions_service import authorize_objects
from sandwich.core.util.http import AuthenticatedHttpRequest
from sandwich.core.util.http import validate_sort

logger = logging.getLogger(__name__)


class CustomAttributeForm(forms.ModelForm[CustomAttribute]):
    class Meta:
        model = CustomAttribute
        fields = ("name",)

    input_type = forms.ChoiceField(
        choices=[
            ("date", "Date"),
            ("select", "Select"),
            ("multi_select", "Multi-Select"),
        ],
        widget=forms.Select(attrs={"class": "form-select"}),
        initial=None,
    )

    def __init__(self, *args, content_type: ContentType, organization: Organization, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.organization = organization
        self.content_type = content_type

        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", "Submit"))

        if self.instance.pk:
            self.initial["input_type"] = self._from_instance(self.instance)
            self.fields["input_type"].widget.attrs["readonly"] = True

    def _from_instance(self, instance: CustomAttribute) -> str | None:
        """Derive 'input_type' field value from instance data."""
        match (instance.data_type, instance.is_multi):
            case (CustomAttribute.DataType.DATE, False):
                return "date"
            case (CustomAttribute.DataType.ENUM, False):
                return "select"
            case (CustomAttribute.DataType.ENUM, True):
                return "multi_select"

    def _from_input_type(self, input_type: str) -> None:
        """Derive model fields from 'input_type' field value."""
        match input_type:
            case "date":
                return (CustomAttribute.DataType.DATE, False)
            case "select":
                return (CustomAttribute.DataType.ENUM, False)
            case "multi_select":
                return (CustomAttribute.DataType.ENUM, True)

    def save(self, commit=True):  # noqa: FBT002
        instance = super().save(commit=False)

        data_type, is_multi = self._from_input_type(self.cleaned_data["input_type"])
        instance.data_type = data_type
        instance.is_multi = is_multi
        instance.content_type = self.content_type
        instance.organization = self.organization

        if commit:
            instance.save()

        return instance


@login_required
@authorize_objects([ObjPerm(Organization, "organization_id", ["change_organization", "view_organization"])])
def custom_attribute_add(request: AuthenticatedHttpRequest, organization: Organization) -> HttpResponse:
    form = CustomAttributeForm(
        request.POST if request.method == "POST" else None,
        # TODO: make dynamic when we support more models
        content_type=ContentType.objects.get_for_model(Encounter),
        organization=organization,
    )
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.add_message(request, messages.SUCCESS, "Custom attribute created successfully.")
        return HttpResponseRedirect(
            reverse(
                "providers:custom_attribute_list",
                kwargs={"organization_id": organization.id},
            )
        )

    context = {
        "organization": organization,
        "form": form,
    }
    return render(request, "provider/custom_attribute_edit.html", context)



@login_required
@authorize_objects([ObjPerm(Organization, "organization_id", ["change_organization", "view_organization"])])
def custom_attribute_list(request: AuthenticatedHttpRequest, organization: Organization) -> HttpResponse:
    page = request.GET.get("page", 1)

    # TODO: permission filtering after defining the rules
    # provider_patients: QuerySet = get_objects_for_user(request.user, "core.view_patient")
    sort = (
        validate_sort(
            request.GET.get("sort"),
            ["name", "created_at", "data_type", "updated_at"],
        )
        or "name"
    )

    attributes = CustomAttribute.objects.all().filter(
        organization=organization, content_type=ContentType.objects.get_for_model(Encounter)
    )
    if sort:
        attributes = attributes.order_by(sort)

    paginator = Paginator(attributes, 25)

    context = {
        "attributes": paginator.get_page(page),
        "organization": organization,
        "sort": sort,
        "page": page,
    }
    if request.headers.get("HX-Request"):
        return render(request, "provider/partials/custom_attribute_list_table.html", context)
    return render(request, "provider/custom_attribute_list.html", context)


@login_required
@authorize_objects([ObjPerm(Organization, "organization_id", ["change_organization", "view_organization"])])
def custom_attribute_add(request: AuthenticatedHttpRequest, organization: Organization) -> HttpResponse:
    return HttpResponse(status=200)


@login_required
@authorize_objects([ObjPerm(Organization, "organization_id", ["change_organization", "view_organization"])])
def custom_attribute_edit(
    request: AuthenticatedHttpRequest, organization: Organization, attribute_id: UUID
) -> HttpResponse:
    return HttpResponse(status=200)


@login_required
@authorize_objects([ObjPerm(Organization, "organization_id", ["change_organization", "view_organization"])])
def custom_attribute_archive(
    request: AuthenticatedHttpRequest, organization: Organization, attribute_id: UUID
) -> HttpResponse:
    return HttpResponse(status=200)
