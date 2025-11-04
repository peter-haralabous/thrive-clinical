import logging
import uuid
from typing import Annotated
from typing import cast

import ninja
from ninja.security import SessionAuth

from sandwich.core.models.task import Task
from sandwich.core.service.permissions_service import get_authorized_object_or_404
from sandwich.core.util.http import AuthenticatedHttpRequest

logger = logging.getLogger(__name__)
router = ninja.Router()
require_login = SessionAuth()


def get_form_for_task(task: Task):
    return task.form_version.schema if task.form_version else {}


@router.get("/{task_id}", auth=require_login)
def get_form(request: AuthenticatedHttpRequest, task_id: uuid.UUID):
    task = cast("Task", get_authorized_object_or_404(request.user, ["view_task"], Task, id=task_id))
    return get_form_for_task(task)


@router.post("/{task_id}/submit", auth=require_login)
def submit_form(request: AuthenticatedHttpRequest, task_id: uuid.UUID, payload: Annotated[dict, ninja.Body(...)]):
    task = cast("Task", get_authorized_object_or_404(request.user, ["view_task", "complete_task"], Task, id=task_id))
    # raise ninja.errors.HttpError(400, "Fake error for testing purposes")

    # TODO: get_or_create form submission record in database
    logger.info(
        "Form submitted",
        extra={"user_id": request.user.id, "task_id": task.id, "payload": payload},
    )
    return {"status": "success", "message": "Form submitted successfully."}
