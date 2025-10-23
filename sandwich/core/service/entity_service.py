from sandwich.core.models import Entity
from sandwich.core.models import Patient
from sandwich.core.models.entity import EntityType


def entity_for_patient(patient: Patient) -> Entity:
    return Entity.objects.get_or_create(
        type=EntityType.PATIENT,
        metadata__patient_id=str(patient.id),
        defaults={
            "type": EntityType.PATIENT,
            "metadata": {"patient_id": str(patient.id), "label": patient.full_name},
        },
    )[0]
