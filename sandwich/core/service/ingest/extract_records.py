import datetime
from typing import cast

import pghistory
import pydantic
from langchain_core.messages import SystemMessage

from sandwich.core.models import Document
from sandwich.core.models import Immunization
from sandwich.core.models import Practitioner
from sandwich.core.service.llm import ModelName
from sandwich.core.service.llm import get_claude_sonnet_4_5


class ImmunizationRecord(pydantic.BaseModel):
    name: str
    date: datetime.date


class PractitionerRecord(pydantic.BaseModel):
    name: str


class RecordsResponse(pydantic.BaseModel):
    immunizations: list[ImmunizationRecord]
    practitioners: list[PractitionerRecord]

    def __len__(self):
        return len(self.immunizations) + len(self.practitioners)


content_type_to_format = {
    "text/plain": "txt",
    "application/pdf": "pdf",
}


def _to_document_block(document: Document) -> dict:
    """
    convert a Document into something that Bedrock can understand

    see https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_DocumentBlock.html
    """
    # TODO: if the file is S3-backed, pass the S3 location instead
    with document.file.open("rb") as f:
        content = f.read()
    source = {"bytes": content}

    return {
        "type": "document",
        "document": {
            # NOTE: AWS recommends not using the original filename to avoid prompt injection
            "name": "document",
            "source": source,
            # "citations": {"enabled": True},
            # "context": "something about this document",
            "format": content_type_to_format[document.content_type],
        },
    }


def _extract_records(document: Document) -> RecordsResponse:
    llm = get_claude_sonnet_4_5()
    return cast(
        "RecordsResponse",
        llm.with_structured_output(RecordsResponse).invoke(
            [
                SystemMessage(
                    content="You are a helpful assistant that extracts medical records from clinical documents."
                ),
                {
                    "role": "user",
                    "content": [
                        _to_document_block(document),
                        {
                            "type": "text",
                            "text": "Extract medical records from the above clinical document.",
                        },
                    ],
                },
            ]
        ),
    )


def _save_records(document: Document, records: RecordsResponse) -> None:
    with pghistory.context(llm=ModelName.CLAUDE_SONNET_4_5, document=document.id):
        for immunization_data in records.immunizations:
            Immunization.objects.get_or_create(
                patient=document.patient,
                name=immunization_data.name,
                date=immunization_data.date,
                defaults={"unattested": True},
            )

        for practitioner_data in records.practitioners:
            Practitioner.objects.get_or_create(
                patient=document.patient, name=practitioner_data.name, defaults={"unattested": True}
            )


def extract_records(document: Document) -> RecordsResponse:
    records = _extract_records(document)
    _save_records(document, records)
    return records
