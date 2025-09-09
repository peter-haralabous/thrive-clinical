from django.urls import path

from sandwich.bread.views.patient import patient
from sandwich.bread.views.patient import patient_add

urlpatterns = [
    path("patient/add", patient_add, name="patient_add"),
    path("patient/<int:pk>", patient, name="patient"),
]
