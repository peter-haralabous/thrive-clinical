from django.db import models

from sandwich.core.models.abstract import BaseModel
from sandwich.core.models.entity import Entity
from sandwich.core.models.predicate import Predicate
from sandwich.core.models.provenance import Provenance


class Fact(BaseModel):
    """
    A fact in the knowledge graph, representing a relationship between two entities via a predicate.
    """

    subject = models.ForeignKey(Entity, related_name="facts_as_subject", on_delete=models.CASCADE)
    predicate = models.ForeignKey(Predicate, on_delete=models.CASCADE)
    object = models.ForeignKey(Entity, related_name="facts_as_object", on_delete=models.CASCADE)
    provenance = models.ForeignKey(
        Provenance,
        null=True,
        blank=True,
        related_name="facts",
        on_delete=models.SET_NULL,
    )
    metadata = models.JSONField(blank=True, null=True, help_text="Additional data about the fact.")

    start_datetime = models.DateTimeField(null=True, blank=True, help_text="The start date and time of the fact.")
    end_datetime = models.DateTimeField(null=True, blank=True, help_text="The end date and time of the fact.")

    def __str__(self):
        return f"{self.subject} {self.predicate} {self.object}"
