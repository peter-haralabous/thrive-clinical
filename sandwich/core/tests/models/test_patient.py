import pytest

from sandwich.core.models import Organization
from sandwich.core.models import Patient


@pytest.mark.django_db
def test_patient_search() -> None:
    o = Organization.objects.create(name="Test Organization")
    p = Patient.objects.create(first_name="John", last_name="Doe", organization=o)

    # don't match this one
    Patient.objects.create(
        first_name="Jane", last_name="Doe", organization=Organization.objects.create(name="Other Organization")
    )

    def search(query: str) -> list[Patient]:
        return list(Patient.objects.filter(organization=o).search(query))  # type: ignore[attr-defined]

    assert search("john") == [p]
    assert search("doe") == [p]
    assert search("john doe") == [p]
    assert search("jane") == []
    assert search("jane doe") == []
