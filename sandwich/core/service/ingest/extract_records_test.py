from pathlib import Path

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.uploadedfile import UploadedFile

from sandwich.core.models import Document
from sandwich.core.models import Patient
from sandwich.core.models import Practitioner
from sandwich.core.models.document import DocumentCategory
from sandwich.core.service.ingest.extract_records import PractitionerRecord
from sandwich.core.service.ingest.extract_records import RecordsResponse
from sandwich.core.service.ingest.extract_records import _save_records
from sandwich.core.service.ingest.extract_records import extract_records


def _document_from_file(patient: Patient, file: UploadedFile) -> Document:
    assert file.name is not None
    assert file.content_type is not None
    return Document.objects.create(
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
    immunization = patient.immunization_set.first()
    assert immunization is not None
    assert immunization.unattested is True
    assert str(immunization.date) == "2000-01-01"


@pytest.mark.vcr
def test_extract_records_from_pdf(patient: Patient):
    dr_susan = Practitioner.objects.create(patient=patient, name="Dr. Susan Albright")

    file = SimpleUploadedFile(
        name="uploaded.pdf",
        content=Path("sandwich/core/fixtures/mock_health_data.pdf").read_bytes(),
        content_type="application/pdf",
    )
    document = _document_from_file(patient, file)
    records = extract_records(document)
    assert len(records.immunizations) == 2
    assert len(records.practitioners) == 1
    assert len(records.conditions) == 2
    assert len(records) == 5

    assert patient.immunization_set.count() == 2

    # created records should be marked as llm-generated
    immunization = patient.immunization_set.first()
    assert immunization is not None
    assert immunization.unattested is True
    assert immunization.get_current_version().pgh_context.metadata == {
        "document": str(document.id),
        "llm": "claude-sonnet-4-5",
    }

    # the pre-existing practitioner shouldn't be duplicated
    assert patient.practitioner_set.count() == 1
    assert dr_susan.get_total_versions() == 1
    assert dr_susan.unattested is False

    assert str(document.date) == "2025-09-12"  # incorrect -- should be 2025-09-16
    assert document.category == DocumentCategory.HEALTH_VISITS
    assert document.unattested is True


def test__save_records(patient: Patient):
    Practitioner.objects.create(patient=patient, name="DR. JOHN SMITH")
    document = Document(patient=patient)
    records = RecordsResponse(
        document_category=DocumentCategory.HEALTH_VISITS,
        document_date=None,
        conditions=[],
        immunizations=[],
        practitioners=[PractitionerRecord(name="Dr. John Smith")],
    )

    _save_records(document, records)

    # we should not have created a second practitioner that differs only by case
    assert len(patient.practitioner_set.all()) == 1
