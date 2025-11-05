from pathlib import Path

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.uploadedfile import UploadedFile

from sandwich.core.models import Document
from sandwich.core.models import Patient
from sandwich.core.models import Practitioner
from sandwich.core.service.ingest.extract_records import extract_records


def _document_from_file(patient: Patient, file: UploadedFile) -> Document:
    assert file.name is not None
    assert file.content_type is not None
    return Document(
        patient=patient, file=file, original_filename=file.name, content_type=file.content_type, size=file.size
    )


@pytest.mark.vcr
def test_extract_records_from_text(patient: Patient):
    file = SimpleUploadedFile(name="uploaded.txt", content=b"Patient received a polio immunization on 2000-01-01.")
    document = _document_from_file(patient, file)
    records = extract_records(document)
    assert len(records.immunizations) == 1
    assert len(records) == 1  # no other records

    assert patient.immunization_set.count() == 1


@pytest.mark.vcr
def test_extract_records_from_pdf(patient: Patient):
    dr_susan = Practitioner.objects.create(patient=patient, name="Dr. Susan Albright")

    file = SimpleUploadedFile(
        name="uploaded.pdf", content=Path("sandwich/core/fixtures/mock_health_data.pdf").read_bytes()
    )
    document = _document_from_file(patient, file)
    records = extract_records(document)
    assert len(records.immunizations) == 3
    assert len(records.practitioners) == 2  # this is an error -- one of the doctors is the patient's spouse

    assert patient.immunization_set.count() == 3

    # created records should be marked as llm-generated
    immunization = patient.immunization_set.first()
    assert immunization is not None
    assert immunization.unattested is True
    assert immunization.get_current_version().pgh_context.metadata == {
        "document": str(document.id),
        "llm": "claude-sonnet-4-5",
    }

    # the pre-existing practitioner shouldn't be duplicated
    assert patient.practitioner_set.count() == 2
    assert dr_susan.get_total_versions() == 1
    assert dr_susan.unattested is False
