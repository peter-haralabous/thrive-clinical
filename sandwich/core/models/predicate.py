from django.db import models

from sandwich.core.models.abstract import BaseModel


class Predicate(BaseModel):
    """
    A named relationship between two entities (e.g. 'has_condition', 'started_medication')
    """

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")

    def __str__(self):
        return self.name
