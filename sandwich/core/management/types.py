from sandwich.core.management.lib.types import model_type
from sandwich.core.models import Patient
from sandwich.core.models import Template


def patient_type(value: str) -> Patient:
    return model_type(Patient, ["id", "email"], value)


def template_type(value: str) -> Template:
    return model_type(Template, ["id", "slug"], value)
