import base64
import logging
from io import BytesIO
from typing import cast

import pydantic
from django.utils import timezone
from langchain_core.language_models import BaseChatModel
from pdf2image import convert_from_bytes
from pdf2image import convert_from_path

from sandwich.core.models import Document
from sandwich.core.models import Patient
from sandwich.core.models import Provenance
from sandwich.core.models.provenance import SourceType
from sandwich.core.service.ingest.db import save_triples
from sandwich.core.service.ingest.prompt import get_ingest_prompt
from sandwich.core.service.ingest.response_models import IngestPromptWithContextResponse
from sandwich.core.service.ingest.schema import PREDICATE_NAMES
from sandwich.core.service.ingest.types import Triple

logger = logging.getLogger(__name__)


def convert_pages(pdf_source: str | bytes) -> list[bytes]:
    """
    Convert each page of a PDF to PNG image bytes (for LLM image input).
    Accepts either a filesystem path or raw PDF bytes.
    """
    source_type = "bytes" if isinstance(pdf_source, bytes | bytearray) else "path"
    logger.info("Converting PDF pages to images", extra={"source_type": source_type})

    if isinstance(pdf_source, bytes | bytearray):
        images = convert_from_bytes(pdf_source, fmt="png")
    else:
        images = convert_from_path(pdf_source, fmt="png")

    page_pngs = []
    for img in images:
        buf = BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        page_pngs.append(buf.getvalue())

    logger.info("Converted PDF pages to images", extra={"page_count": len(page_pngs), "source_type": source_type})
    return page_pngs


def _build_image_messages(page_index: int, base64_img: str) -> list:
    prompt = get_ingest_prompt(
        input_text="[See attached image of clinical document page]",
        input_description=f"This is page {page_index} of a scanned clinical document.",
    )
    return [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_img}"}},
            ],
        }
    ]


def _process_response(
    response: IngestPromptWithContextResponse, patient: Patient | None, page_index: int
) -> list[Triple]:
    """
    Process LLM response to extract and validate triples, filtering out invalid ones.
    """
    patient_id = str(patient.id) if patient else None
    try:
        triples = response.triples
        logger.info(
            "Processing LLM response triples",
            extra={"total_triples": len(triples), "page_index": page_index, "patient_id": patient_id},
        )

        filtered_triples: list = []
        for t in triples:
            pred = getattr(t, "normalized_predicate", None)
            pred_label = pred.predicate_type if (pred is not None and hasattr(pred, "predicate_type")) else pred
            if pred_label not in set(PREDICATE_NAMES):
                logger.warning(
                    "Dropping triple with out-of-schema predicate",
                    extra={"predicate": pred_label, "page_index": page_index, "patient_id": patient_id},
                )
                continue
            t.subject.node["patient_id"] = str(getattr(patient, "id", "-1"))
            filtered_triples.append(t)

        logger.info(
            "Processed and filtered triples",
            extra={
                "total_triples": len(triples),
                "filtered_triples": len(filtered_triples),
                "dropped_triples": len(triples) - len(filtered_triples),
                "page_index": page_index,
                "patient_id": patient_id,
            },
        )
    except (TypeError, AttributeError, pydantic.ValidationError, ValueError):
        logger.exception(
            "Could not validate structured triples",
            extra={"page_index": page_index, "patient_id": patient_id},
        )
        return []
    else:
        return filtered_triples


def extract_facts_from_pdf(
    pdf_source: str | bytes,
    llm_client: BaseChatModel,
    document: Document | None = None,
    patient: Patient | None = None,
) -> list:
    """
    PDF image-based triple extraction pipeline.
        - Convert PDF pages to images.
        - For each page image, build LLM messages and invoke LLM.
        - Process and validate LLM response as triples.
        - Persist valid triples to DB.
        - Returns all extracted triples across pages.
    """
    document_id = str(document.id) if document else None
    patient_id = str(patient.id) if patient else None
    llm_name = llm_client.__class__.__name__

    logger.info(
        "Starting PDF fact extraction",
        extra={
            "document_id": document_id,
            "patient_id": patient_id,
            "llm_name": llm_name,
        },
    )

    structured_llm_client = llm_client.with_structured_output(
        schema=IngestPromptWithContextResponse, method="json_mode"
    )

    images = convert_pages(pdf_source)
    all_triples: list = []
    for i, image_bytes in enumerate(images, start=1):
        logger.info(
            "Processing PDF page",
            extra={
                "page_index": i,
                "total_pages": len(images),
                "document_id": document_id,
                "patient_id": patient_id,
            },
        )

        base64_img = base64.b64encode(image_bytes).decode("utf-8")
        messages = _build_image_messages(i, base64_img)
        try:
            response = cast("IngestPromptWithContextResponse", structured_llm_client.invoke(messages))
            triples_to_save = _process_response(response, patient, i)
            if triples_to_save:
                provenance = Provenance.objects.create(
                    document=document,
                    page=i,
                    source_type=SourceType.DOCUMENT if document else SourceType.UNKNOWN,
                    extracted_at=timezone.now(),
                    extracted_by=llm_client.__class__.__name__,
                )
                save_triples(triples_to_save, provenance, patient=patient)
                all_triples.extend(triples_to_save)
                logger.info(
                    "Saved triples from page",
                    extra={
                        "page_index": i,
                        "triples_saved": len(triples_to_save),
                        "provenance_id": str(provenance.id),
                        "document_id": document_id,
                        "patient_id": patient_id,
                    },
                )
            else:
                logger.info(
                    "No valid triples extracted from page",
                    extra={"page_index": i, "document_id": document_id, "patient_id": patient_id},
                )
        except (ValueError, TypeError, AttributeError, RuntimeError, ConnectionError, TimeoutError, OSError):
            logger.exception(
                "Failed to extract triples from page",
                extra={
                    "page_index": i,
                    "total_pages": len(images),
                    "document_id": document_id,
                    "patient_id": patient_id,
                },
            )
            continue

    logger.info(
        "Completed PDF fact extraction",
        extra={
            "total_triples": len(all_triples),
            "total_pages": len(images),
            "document_id": document_id,
            "patient_id": patient_id,
            "llm_name": llm_name,
        },
    )
    return all_triples
