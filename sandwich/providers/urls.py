from django.urls import path

from .views.home import home
from .views.organization import organization_add
from .views.organization import organization_edit
from .views.patient import organization_patient_list
from .views.patient import patient_add
from .views.patient import patient_edit

app_name = "providers"
urlpatterns = [
    path("", home, name="home"),
    path("patient/<int:patient_id>", patient_edit, name="patient"),
    path("organization/<int:organization_id>/patient/<int:patient_id>", patient_edit, name="organization_patient"),
    path("organization/<int:organization_id>/patients", organization_patient_list, name="patient_list"),
    path("organization/<int:organization_id>/patient/add", patient_add, name="patient_add"),
    path("organization/add", organization_add, name="organization_add"),
    path("organization/<int:organization_id>", organization_edit, name="organization"),
]
