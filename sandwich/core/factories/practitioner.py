import factory

from sandwich.core.factories.health_record import HealthRecordFactory
from sandwich.core.models import Practitioner


class PractitionerFactory(HealthRecordFactory):
    class Meta:
        model = Practitioner

    name = factory.Faker("name")
