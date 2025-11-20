from pathlib import Path

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from sandwich.core.factories.form import FormFactory
from sandwich.core.service.form_generation.generate_form import DocType
from sandwich.core.service.form_generation.generate_form import generate_form_schema_from_reference_file
from sandwich.core.service.form_generation.prompt import form_from_csv
from sandwich.core.service.form_generation.prompt import form_from_pdf


@pytest.mark.vcr
@pytest.mark.django_db(transaction=True)
def test_generate_form_schema_simple_pdf() -> None:
    pdf_bytes = Path("sandwich/core/fixtures/simple_pdf_form.pdf").read_bytes()
    pdf = SimpleUploadedFile(name="simple_pdf_form.pdf", content=pdf_bytes, content_type="application/pdf")

    prompt = form_from_pdf()
    form = FormFactory.create(name="test_pdf_form", schema={"title": "Test"}, reference_file=pdf)

    generate_form_schema_from_reference_file(form=form, doc_type=DocType.PDF, text_prompt=prompt)

    form.refresh_from_db()
    assert form.schema["pages"][0]["elements"]
    assert form.schema["pages"][0]["elements"][0].get("type") == "text"
    assert form.schema["pages"][0]["elements"][0].get("title") == "First name"


@pytest.mark.vcr
@pytest.mark.django_db(transaction=True)
def test_generate_form_schema_simple_csv() -> None:
    csv_bytes = b"""
    title,Simple Form
    q1, First name, textfield
    """
    csv = SimpleUploadedFile(name="simple_form.csv", content=csv_bytes, content_type="text/csv")

    prompt = form_from_csv()
    form = FormFactory.create(name="test_csv_form", schema={"title": "Test"}, reference_file=csv)

    generate_form_schema_from_reference_file(form=form, doc_type=DocType.CSV, text_prompt=prompt)

    form.refresh_from_db()
    assert form.schema["pages"][0]["elements"]
    assert form.schema["pages"][0]["elements"][0].get("type") == "text"
    assert form.schema["pages"][0]["elements"][0].get("title") == "First name"
