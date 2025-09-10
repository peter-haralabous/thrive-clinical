from django.urls import path

from .views.home import home
from .views.patient import patient
from .views.patient import patient_add

app_name = "providers"
urlpatterns = [
    path("", home, name="home"),
    path("patient/add", patient_add, name="patient_add"),
    path("patient/<int:pk>", patient, name="patient"),
]
