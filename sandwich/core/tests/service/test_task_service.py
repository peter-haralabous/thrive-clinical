import pytest

from sandwich.core.models import Task
from sandwich.core.service.task_service import send_task_added_email
from sandwich.core.tests.service.test_invitation_service import mask_uuids


@pytest.mark.django_db
def test_send_task_added_email(task: Task, mailoutbox, snapshot):
    send_task_added_email(task)
    assert len(mailoutbox) == 1
    assert mailoutbox[0].to == [task.patient.email]

    # if the template changes, the snapshot will need to be updated
    assert mask_uuids(mailoutbox[0].body) == snapshot
