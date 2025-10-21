import enum
import typing

from django.db import models
from django_enum import EnumField

from sandwich.core.models.abstract import BaseModel

if typing.TYPE_CHECKING:
    from sandwich.core.models import Patient


class EntityType(enum.Enum):
    PATIENT = "Patient"
    CONDITION = "Condition"
    MEDICATION = "Medication"
    OBSERVATION = "Observation"
    ALLERGY_INTOLERANCE = "AllergyIntolerance"
    IMMUNIZATION = "Immunization"
    PROCEDURE = "Procedure"
    FAMILY_MEMBER = "FamilyMember"


class Entity(BaseModel):
    """
    A node in the knowledge graph (e.g. patient, symptom, drug, place, etc.)
    """

    type: models.Field[EntityType, EntityType] = EnumField(
        EntityType, null=True, blank=True, help_text="Type of the entity in the knowledge graph."
    )
    metadata = models.JSONField(blank=True, null=True, help_text="e.g., FHIR codes, LOINC, etc.")

    class Meta:
        verbose_name = "Entity"
        verbose_name_plural = "Entities"
        constraints = [
            models.UniqueConstraint(
                models.F("metadata__patient_id"),
                name="unique_patient_id_in_metadata",
                condition=(models.Q(metadata__has_key="patient_id") & models.Q(type=EntityType.PATIENT.value)),
            )
        ]

    def __str__(self) -> str:
        if self.metadata and "label" in self.metadata:
            return str(self.metadata["label"])
        return str(self.pk)

    @staticmethod
    def for_patient(patient: "Patient") -> "Entity":
        return Entity.objects.get_or_create(
            type=EntityType.PATIENT,
            metadata__patient_id=str(patient.id),
            defaults={
                "type": EntityType.PATIENT,
                "metadata": {"patient_id": str(patient.id), "label": patient.full_name},
            },
        )[0]
