import factory
from factory.django import DjangoModelFactory

from sandwich.core.models import Patient
from sandwich.core.service.patient_service import assign_default_provider_patient_permissions


class PatientFactory(DjangoModelFactory[Patient]):
    class Meta:
        model = Patient

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    date_of_birth = factory.Faker("date_of_birth")

    @factory.post_generation
    def set_permissions(obj: Patient, create, extracted, **kwargs):  # noqa: N805
        """Assign default permissions after the patient is created."""
        if not create:
            return
        assign_default_provider_patient_permissions(obj)
