import logging
from uuid import UUID

from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render

from sandwich.core.models.custom_attribute import CustomAttribute
from sandwich.core.models.encounter import Encounter
from sandwich.core.models.organization import Organization
from sandwich.core.service.permissions_service import ObjPerm
from sandwich.core.service.permissions_service import authorize_objects
from sandwich.core.util.http import AuthenticatedHttpRequest
from sandwich.core.util.http import validate_sort

logger = logging.getLogger(__name__)


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
