import logging

# from procrastinate.contrib.django import app

logger = logging.getLogger(__name__)


# Tasks go here.
# https://procrastinate.readthedocs.io/en/stable/howto/basics/tasks.html

# If the task has a better suited place, put it there instead of here.
# For Procrastinate to find your task(s), make sure that the module is
# listed in the PROCRASTINATE_IMPORT_PATHS setting or that it is in an
# autodiscovered module. By default, procrastinate looks for tasks.py
# in a django app, or is set with PROCRASTINATE_AUTODISCOVER_MODULE_NAME
# https://procrastinate.readthedocs.io/en/stable/howto/django/settings.html#customize-the-app-integration-through-settings


# Periodic tasks.
# https://procrastinate.readthedocs.io/en/stable/howto/advanced/cron.html#launch-a-task-periodically

# Uncomment the following to have a periodic task that runs every 5 minutes.
# @app.periodic(cron="*/5 * * * *")  # every 5 mins
# @app.task
# def dummy_task(timestamp: int):
#     logger.info("I'm a working worker.")
