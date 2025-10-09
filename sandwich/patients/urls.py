from django.urls import path

from .api import api
from .views.home import home
from .views.invitation import accept_invite
from .views.patient import patient_add
from .views.patient import patient_details
from .views.patient import patient_edit
from .views.task import task

app_name = "patients"
urlpatterns = [
    path("", home, name="home"),
    path("patient/add", patient_add, name="patient_add"),
    path("patient/<uuid:patient_id>", patient_details, name="patient_details"),
    path("patient/<uuid:patient_id>/edit", patient_edit, name="patient_edit"),
    path("invite/<str:token>/accept", accept_invite, name="accept_invite"),
    path("patient/<uuid:patient_id>/task/<uuid:task_id>", task, name="task"),
    path("api/", api.urls, name="api"),
]
