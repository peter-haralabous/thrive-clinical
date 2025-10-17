import logging

from sandwich.core.services.ingest.types import Triple

logger = logging.getLogger(__name__)


def save_triples(
    triples: list[Triple],
    patient=None,
    source_type: str | None = None,
) -> int:
    return 0
