from django.db import models

from sandwich.core.models.abstract import BaseModel
from sandwich.core.models.organization import Organization
from sandwich.users.models import User


# Specifies an organization is authorized to interact with patients (PHI)
class OrganizationVerification(BaseModel):
    organization = models.OneToOneField(Organization, on_delete=models.CASCADE)
    approver = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={"is_staff": True})
