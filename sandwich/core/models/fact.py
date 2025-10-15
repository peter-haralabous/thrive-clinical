from django.db import models

from sandwich.core.models.abstract import BaseModel
from sandwich.core.models.entity import Entity
from sandwich.core.models.predicate import Predicate


class Fact(BaseModel):
    """
    A fact in the knowledge graph, representing a relationship between two entities via a predicate.
    """

    subject = models.ForeignKey(Entity, related_name="facts_as_subject", on_delete=models.CASCADE)
    predicate = models.ForeignKey(Predicate, on_delete=models.CASCADE)
    object = models.ForeignKey(Entity, related_name="facts_as_object", on_delete=models.CASCADE)
    # TODO-RG: Add provenance
    # TODO-RG: Add status/validity field (e.g., active, inactive)
    # TODO-RG: Add patient reference if needed
    metadata = models.JSONField(blank=True, null=True, help_text="Additional data about the fact.")

    def __str__(self):
        return f"{self.subject} {self.predicate} {self.object}"
