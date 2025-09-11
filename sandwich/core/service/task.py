from datetime import UTC
from datetime import datetime

from sandwich.core.models.task import Task
from sandwich.core.models.task import TaskStatus


def cancel_task(task: Task) -> None:
    """Cancel a pending task."""
    assert task.active, "Task is not active"
    task.status = TaskStatus.CANCELLED
    task.ended_at = datetime.now(UTC)
    task.save()
