from __future__ import annotations

import pydantic


class Entity(pydantic.BaseModel):
    entity_type: str
    node: dict[str, object]


class NormalizedPredicate(pydantic.BaseModel):
    predicate_type: str
    traits: dict[str, bool] | None = None
    properties: dict[str, object] | None = None


class Triple(pydantic.BaseModel):
    subject: Entity
    predicate: str
    normalized_predicate: NormalizedPredicate
    object: Entity
    provenance: dict[str, object] | None = None  # type: ignore[valid-type]
