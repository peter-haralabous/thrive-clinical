import logging
import uuid
from typing import Annotated
from typing import cast

import ninja
from django.db import IntegrityError
from django.http import JsonResponse
from ninja.errors import HttpError
from ninja.security import SessionAuth

from sandwich.core.models.form import Form
from sandwich.core.models.organization import Organization
from sandwich.core.service.permissions_service import get_authorized_object_or_404
from sandwich.core.util.http import AuthenticatedHttpRequest

logger = logging.getLogger(__name__)
router = ninja.Router()
require_login = SessionAuth()


class FormSavedResponse(JsonResponse):
    """
    A custom JsonResponse for saving a form.
    """

    @classmethod
    def success(cls, form: Form, message: str, **kwargs) -> "FormSavedResponse":
        data = {
            "result": "success",
            "message": message,
            "form_id": str(form.id),
        }
        return cls(data, **kwargs)


@router.post("/organization/{organization_id}/form/{form_id}/edit", auth=require_login)
def edit_form(
    request: AuthenticatedHttpRequest,
    organization_id: uuid.UUID,
    form_id: uuid.UUID,
    payload: Annotated[dict, ninja.Body(...)],
) -> FormSavedResponse:
    logger.info(
        "Provider API: Form edit accessed",
        extra={"user_id": request.user.id, "organization_id": organization_id, "form_id": form_id, "payload": payload},
    )
    # Ensure permissions enforced.
    # Not checking Org 'create_form' since this is change, not create.
    organization = cast(
        "Organization",
        get_authorized_object_or_404(request.user, ["view_organization"], Organization, id=organization_id),
    )
    form = cast("Form", get_authorized_object_or_404(request.user, ["view_form", "change_form"], Form, id=form_id))

    # Validation: Guard against empty title in payload as Form.name is required.
    name = payload.get("title", None)
    if not name:
        logger.info(
            "Form update failed: form title missing in schema",
            extra={"user_id": request.user.id, "organization_id": organization_id, "form_id": form.id},
        )
        raise HttpError(400, "Form must include a title: 'General' section missing 'Survey title'")

    try:
        Form.objects.filter(pk=form.id).update(schema=payload, name=name)
    except IntegrityError as ex:
        logger.info(
            "Form update failed: Form with same name exists in organization",
            extra={
                "user_id": request.user.id,
                "organization_id": organization_id,
                "form_id": form.id,
                "form_name": name,
            },
        )
        raise HttpError(400, "Form with the same title already exists. Please choose a different title.") from ex

    logger.info(
        "Form changes saved",
        extra={
            "user_id": request.user.id,
            "organization_id": organization.id,
            "form_id": form.id,
            "form_name": form.name,  # should not contain PHI.
        },
    )
    return FormSavedResponse.success(form=form, message="Form saved successfully")


@router.post("/organization/{organization_id}/create", auth=require_login)
def create_form(
    request: AuthenticatedHttpRequest, organization_id: uuid.UUID, payload: Annotated[dict, ninja.Body(...)]
) -> FormSavedResponse:
    logger.info(
        "Provider API: Form create accessed",
        extra={"user_id": request.user.id, "organization_id": organization_id, "payload": payload},
    )
    organization = cast(
        "Organization", get_authorized_object_or_404(request.user, ["create_form"], Organization, id=organization_id)
    )

    # Validation: Guard against empty title in payload as Form.name is required.
    name = payload.get("title", None)
    if not name:
        logger.info(
            "Form creation failed: form title missing in schema",
            extra={"user_id": request.user.id, "organization_id": organization_id},
        )
        raise HttpError(400, "Form must include a title: 'General' section missing 'Survey title'")

    try:
        form = Form.objects.create(organization=organization, name=name, schema=payload)
    except IntegrityError as ex:
        logger.info(
            "Form creation failed: Form with same name exists in organization",
            extra={"user_id": request.user.id, "organization_id": organization_id, "form_name": name},
        )
        raise HttpError(400, "Form with the same title already exists. Please choose a different title.") from ex

    logger.info(
        "Form created in organization",
        extra={
            "user_id": request.user.id,
            "organization_id": organization.id,
            "form_id": form.id,
            "form_name": form.name,  # should not contain PHI.
        },
    )
    return FormSavedResponse.success(form=form, message="Form created successfully")
