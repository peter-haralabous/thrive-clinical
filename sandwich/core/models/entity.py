from django.db import models

from sandwich.core.models.abstract import BaseModel


class Entity(BaseModel):
    """
    A node in the knowledge graph (e.g. patient, symptom, drug, place, etc.)
    """

    type = models.CharField(max_length=100, help_text="e.g., 'person', 'medication'")
    metadata = models.JSONField(blank=True, null=True, help_text="e.g., FHIR codes, LOINC, etc.")

    class Meta:
        verbose_name = "Entity"
        verbose_name_plural = "Entities"
        constraints = [
            models.UniqueConstraint(
                models.F("metadata__patient_id"),
                name="unique_patient_id_in_metadata",
                condition=models.Q(metadata__has_key="patient_id"),
            )
        ]

    def __str__(self) -> str:
        return str(self.pk)
