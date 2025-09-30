import factory
from factory.django import DjangoModelFactory

from sandwich.core.models import Organization
from sandwich.core.service.organization_service import create_default_roles


class OrganizationFactory(DjangoModelFactory):
    class Meta:
        model = Organization

    name = factory.Faker("company")

    @factory.post_generation
    def create_roles(self: Organization, create, extracted, **kwargs):
        create_default_roles(self)
