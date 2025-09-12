from django.apps import AppConfig

import sandwich.core.util.crispy  # noqa: F401


class BreadConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "sandwich.core"
