from django.urls import path

from sandwich.core.views import healthcheck

app_name = "core"
urlpatterns = [
    path("healthcheck/", healthcheck.healthcheck, name="healthcheck"),
]
