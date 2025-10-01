import pytest
from django.db import IntegrityError
from django.db import transaction

from sandwich.core.models import Entity


@pytest.mark.django_db(transaction=True)
def test_entity_unique_patient_id():
    # Create an entity with a patient_id in metadata
    e1 = Entity.objects.create(type="person", metadata={"patient_id": "abc"})
    assert e1.pk is not None

    # Creating another entity with the same patient_id should fail
    with pytest.raises(IntegrityError), transaction.atomic():
        Entity.objects.create(type="person", metadata={"patient_id": "abc"})

    # Creating another entity with a different patient_id should succeed
    e2 = Entity.objects.create(type="person", metadata={"patient_id": "def"})
    assert e2.pk is not None

    # Creating an entity without patient_id in metadata should succeed
    e3 = Entity.objects.create(type="person", metadata={})
    assert e3.pk is not None
