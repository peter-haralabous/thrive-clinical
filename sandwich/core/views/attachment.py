import logging

from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import HttpResponseForbidden
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.views.decorators.http import require_http_methods
from django.views.decorators.http import require_POST
from django_jsonform.views import login_required

from sandwich.core.models.attachment import Attachment
from sandwich.core.util.http import AuthenticatedHttpRequest

logger = logging.getLogger(__name__)


@require_POST
@login_required
def attachment_upload(request: AuthenticatedHttpRequest) -> HttpResponse:
    uploaded_files = request.FILES.getlist("file-upload")
    if not uploaded_files:
        return HttpResponseBadRequest("No file was uploaded.")

    response = []
    for uploaded in uploaded_files:
        # TODO: do we have a file size limit imposed on the infra side?
        if uploaded.size and uploaded.size > 10 * 1024 * 1024:  # 10MB
            return HttpResponseBadRequest("File is too large.")

        attachment = Attachment.objects.create(
            file=uploaded,
            uploaded_by=request.user,
            original_filename=uploaded.name or "untitled",
            content_type=uploaded.content_type or "application/octet-stream",
        )
        response.append(
            {
                "id": attachment.pk,
                "url": attachment.file.url,
                "original_filename": attachment.original_filename,
                "content_type": attachment.content_type,
            }
        )

    return JsonResponse(response, safe=False)  # safe=False allows us to pass an array back instead of a dict


@require_http_methods(["DELETE"])
@login_required
def attachment_delete(request: AuthenticatedHttpRequest) -> HttpResponse:
    attachment_id = request.GET.get("id")
    if not attachment_id or attachment_id == "undefined":
        return HttpResponseBadRequest("Missing or invalid 'id' query parameter.")

    try:
        attachment = Attachment.objects.get(pk=attachment_id, uploaded_by=request.user)
    except (Attachment.DoesNotExist, ValidationError):
        return HttpResponseForbidden()

    if request.user.id == attachment.uploaded_by.id and attachment.uploaded_by.has_perm(
        "delete_attachment", attachment
    ):
        attachment.delete()
        return HttpResponse(status=204)

    return HttpResponseForbidden()


@require_GET
@login_required
def attachment_get(request: AuthenticatedHttpRequest) -> HttpResponse:
    attachment_id = request.GET.get("id")
    if not attachment_id or attachment_id == "undefined":
        return HttpResponseBadRequest("Missing or invalid 'id' query parameter.")

    try:
        attachment = Attachment.objects.get(pk=attachment_id, uploaded_by=request.user)
    except (Attachment.DoesNotExist, ValidationError):
        return HttpResponseForbidden()

    if attachment.uploaded_by.has_perm("view_attachment", attachment):
        response = HttpResponse(attachment.file.read(), content_type=attachment.content_type)
        response["Content-Disposition"] = f'inline; filename="{attachment.original_filename}"'
        return response

    return HttpResponseForbidden()
