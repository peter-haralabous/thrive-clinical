import logging

from procrastinate.contrib.django import app

from sandwich.core.service import invitation_service

logger = logging.getLogger(__name__)


# Tasks go here.
# https://procrastinate.readthedocs.io/en/stable/howto/basics/tasks.html
# https://procrastinate.readthedocs.io/en/stable/howto/advanced/cron.html#launch-a-task-periodically

# If the task has a better suited place, put it there instead of here.
# For Procrastinate to find your task(s), make sure that the module is
# listed in the PROCRASTINATE_IMPORT_PATHS setting or that it is in an
# autodiscovered module. By default, procrastinate looks for tasks.py
# in a django app, or is set with PROCRASTINATE_AUTODISCOVER_MODULE_NAME
# https://procrastinate.readthedocs.io/en/stable/howto/django/settings.html#customize-the-app-integration-through-settings


@app.periodic(cron="0 2 * * *")  # every day at 2am
@app.task(lock="expire_invitations_lock")
def expire_invitations_job(timestamp: int) -> None:
    expired_count = invitation_service.expire_invitations()
    logger.info("Expired %d invitations", expired_count)
