import logging
from datetime import date
from typing import Any
from uuid import UUID

from django.contrib.contenttypes.models import ContentType
from django.db.models import Exists
from django.db.models import Model
from django.db.models import OuterRef
from django.db.models import Q
from django.db.models import QuerySet
from django.db.models import Subquery

from sandwich.core.models import CustomAttribute
from sandwich.core.models import CustomAttributeValue
from sandwich.core.models import Organization

logger = logging.getLogger(__name__)


def _get_annotation_field_name(attribute_id: UUID) -> str:
    """Format a safe annotation field name for a custom attribute."""
    return f"attr_{str(attribute_id).replace('-', '_')}"


def _parse_custom_attribute_id(column_value: str) -> UUID | None:
    """
    Parse custom attribute ID from column value.

    Model field names (like 'patient__first_name') will fail UUID validation
    and return None.
    """
    try:
        return UUID(column_value)
    except (ValueError, AttributeError):
        # Not a UUID - this is a regular model field
        return None


def annotate_custom_attributes[ModelT: Model](
    queryset: QuerySet[ModelT],
    visible_columns: list[str],
    organization: Organization,
    content_type: ContentType,
) -> QuerySet[ModelT]:
    """
    Annotate queryset with custom attribute values for visible columns.

    Only annotates custom attributes in the visible_columns list.
    Uses subqueries to fetch values based on attribute data type.
    """
    custom_columns = [col for col in visible_columns if _parse_custom_attribute_id(col) is not None]

    if not custom_columns:
        logger.debug("No custom attributes to annotate")
        return queryset

    attributes = CustomAttribute.objects.filter(
        organization=organization,
        content_type=content_type,
    ).in_bulk()

    annotations = {}

    for column_value in custom_columns:
        attr_id = _parse_custom_attribute_id(column_value)
        if attr_id is None:
            continue

        attribute = attributes.get(attr_id)
        if not attribute:
            logger.warning(
                "Custom attribute not found, skipping annotation",
                extra={
                    "attribute_id": str(attr_id),
                    "organization_id": organization.id,
                },
            )
            continue

        annotation_name = _get_annotation_field_name(attr_id)

        if attribute.data_type == CustomAttribute.DataType.DATE:
            subquery = Subquery(
                CustomAttributeValue.objects.filter(
                    attribute_id=attr_id,
                    content_type=content_type,
                    object_id=OuterRef("pk"),
                ).values("value_date")[:1]
            )
        elif attribute.data_type == CustomAttribute.DataType.ENUM:
            subquery = Subquery(
                CustomAttributeValue.objects.filter(
                    attribute_id=attr_id,
                    content_type=content_type,
                    object_id=OuterRef("pk"),
                )
                .select_related("value_enum")
                .values("value_enum__label")[:1]
            )
        else:
            logger.warning(
                "Unsupported data type for custom attribute",
                extra={
                    "attribute_id": str(attr_id),
                    "data_type": attribute.data_type,
                },
            )
            continue

        annotations[annotation_name] = subquery
        logger.debug(
            "Added annotation for custom attribute",
            extra={
                "attribute_id": str(attr_id),
                "attribute_name": attribute.name,
                "annotation_name": annotation_name,
            },
        )

    if annotations:
        queryset = queryset.annotate(**annotations)
        logger.info(
            "Annotated queryset with custom attributes",
            extra={
                "organization_id": organization.id,
                "num_annotations": len(annotations),
            },
        )

    return queryset


def apply_sort_with_custom_attributes[ModelT: Model](
    queryset: QuerySet[ModelT],
    sort_field: str,
    organization: Organization,
    content_type: ContentType,
) -> QuerySet[ModelT]:
    """
    Apply sorting to queryset, handling custom attributes.

    If sort_field is a custom attribute, annotates the queryset and sorts by annotation.
    Otherwise, applies standard order_by.
    """
    if not sort_field:
        return queryset

    descending = sort_field.startswith("-")
    field_name = sort_field.lstrip("-")

    attr_id = _parse_custom_attribute_id(field_name)

    if attr_id:
        logger.debug(
            "Applying custom attribute sort",
            extra={
                "sort_field": sort_field,
                "attribute_id": str(attr_id),
            },
        )

        annotation_name = _get_annotation_field_name(attr_id)
        if annotation_name not in queryset.query.annotations:
            queryset = annotate_custom_attributes(
                queryset,
                [field_name],
                organization,
                content_type,
            )

        sort_by = f"-{annotation_name}" if descending else annotation_name
        queryset = queryset.order_by(sort_by)
    else:
        queryset = queryset.order_by(sort_field)

    return queryset


def _build_enum_filter(
    attribute: CustomAttribute,
    filter_config: dict[str, Any],
    annotation_name: str,
    content_type: ContentType,
) -> Q:
    """Build query filter for ENUM attributes using annotation (single-value) or Exists (multi-value)."""
    values = filter_config.get("values", [])
    if not values:
        logger.debug("Empty enum filter values, returning no-op filter")
        return Q()

    include_null = filter_config.get("include_null", False)

    if attribute.is_multi:
        logger.debug(
            "Building multi-value enum filter",
            extra={
                "attribute_id": str(attribute.id),
                "values": values,
            },
        )
        filter_q = Q(
            Exists(
                CustomAttributeValue.objects.filter(
                    attribute_id=attribute.id,
                    content_type=content_type,
                    object_id=OuterRef("pk"),
                    value_enum__value__in=values,
                )
            )
        )
    else:
        logger.debug(
            "Building single-value enum filter",
            extra={
                "attribute_id": str(attribute.id),
                "annotation_name": annotation_name,
                "values": values,
            },
        )
        filter_q = Q(
            **{
                f"{annotation_name}__in": list(
                    CustomAttributeValue.objects.filter(attribute_id=attribute.id, value_enum__value__in=values)
                    .select_related("value_enum")
                    .values_list("value_enum__label", flat=True)
                    .distinct()
                )
            }
        )

    if include_null:
        filter_q |= Q(**{f"{annotation_name}__isnull": True})

    return filter_q


def _normalize_date(date_value: str | date | None) -> date | None:
    """Convert string to date object if needed, return None if value is None."""
    if date_value is None:
        return None
    if isinstance(date_value, str):
        return date.fromisoformat(date_value)
    return date_value


def _build_exact_date_filter(value: str | date | None, annotation_name: str) -> Q:
    """Build exact match date filter."""
    normalized_date = _normalize_date(value)
    if normalized_date:
        return Q(**{annotation_name: normalized_date})
    return Q()


def _build_gte_date_filter(value: str | date | None, annotation_name: str) -> Q:
    """Build greater-than-or-equal date filter."""
    normalized_date = _normalize_date(value)
    if normalized_date:
        return Q(**{f"{annotation_name}__gte": normalized_date})
    return Q()


def _build_lte_date_filter(value: str | date | None, annotation_name: str) -> Q:
    """Build less-than-or-equal date filter."""
    normalized_date = _normalize_date(value)
    if normalized_date:
        return Q(**{f"{annotation_name}__lte": normalized_date})
    return Q()


def _build_range_date_filter(
    start: str | date | None,
    end: str | date | None,
    annotation_name: str,
) -> Q:
    """Build date range filter with support for partial ranges."""
    start_date = _normalize_date(start)
    end_date = _normalize_date(end)

    if start_date and end_date:
        return Q(**{f"{annotation_name}__gte": start_date, f"{annotation_name}__lte": end_date})
    if start_date:
        return Q(**{f"{annotation_name}__gte": start_date})
    if end_date:
        return Q(**{f"{annotation_name}__lte": end_date})
    return Q()


def _build_date_filter(
    attribute: CustomAttribute,
    filter_config: dict[str, Any],
    annotation_name: str,
) -> Q:
    """Build Q filter for DATE attributes supporting exact, gte, lte, and range operators."""
    operator = filter_config.get("operator", "exact")
    include_null = filter_config.get("include_null", False)

    logger.debug(
        "Building date filter",
        extra={
            "attribute_id": str(attribute.id),
            "annotation_name": annotation_name,
            "operator": operator,
        },
    )

    if operator == "exact":
        filter_q = _build_exact_date_filter(filter_config.get("value"), annotation_name)
    elif operator == "gte":
        filter_q = _build_gte_date_filter(filter_config.get("value"), annotation_name)
    elif operator == "lte":
        filter_q = _build_lte_date_filter(filter_config.get("value"), annotation_name)
    elif operator == "range":
        filter_q = _build_range_date_filter(
            filter_config.get("start"),
            filter_config.get("end"),
            annotation_name,
        )
    else:
        filter_q = Q()

    if include_null:
        filter_q |= Q(**{f"{annotation_name}__isnull": True})

    return filter_q


def _build_custom_attribute_filter(
    attribute_id: UUID,
    filter_config: dict[str, Any],
    organization: Organization,
    content_type: ContentType,
    queryset: QuerySet,
) -> Q | None:
    """Build Q filter for a custom attribute, delegating to type-specific builders."""
    try:
        attribute = CustomAttribute.objects.select_related("organization").get(
            id=attribute_id, organization=organization, content_type=content_type
        )
    except CustomAttribute.DoesNotExist:
        logger.warning(
            "Custom attribute not found for filtering",
            extra={
                "attribute_id": str(attribute_id),
                "organization_id": organization.id,
                "content_type": content_type.model,
            },
        )
        return None

    annotation_name = _get_annotation_field_name(attribute_id)

    logger.debug(
        "Building custom attribute filter",
        extra={
            "attribute_id": str(attribute_id),
            "attribute_name": attribute.name,
            "data_type": attribute.data_type,
        },
    )

    if attribute.data_type == CustomAttribute.DataType.ENUM:
        return _build_enum_filter(attribute, filter_config, annotation_name, content_type)
    if attribute.data_type == CustomAttribute.DataType.DATE:
        return _build_date_filter(attribute, filter_config, annotation_name)
    logger.warning(
        "Unsupported data type for custom attribute filter",
        extra={
            "attribute_id": str(attribute_id),
            "data_type": attribute.data_type,
        },
    )
    return None


def apply_filters_with_custom_attributes[ModelT: Model](  # noqa: C901
    queryset: QuerySet[ModelT],
    filters: dict[str, Any],
    organization: Organization,
    content_type: ContentType,
) -> QuerySet[ModelT]:
    """Apply filters to queryset, handling both model fields and custom attributes."""
    if not filters:
        logger.debug("No filters provided, returning unmodified queryset")
        return queryset

    custom_attr_filters = filters.get("custom_attributes", {})
    model_field_filters = filters.get("model_fields", {})

    logger.debug(
        "Applying filters",
        extra={
            "organization_id": organization.id,
            "num_custom_filters": len(custom_attr_filters),
            "num_model_filters": len(model_field_filters),
        },
    )

    if custom_attr_filters:
        attrs_to_annotate = []
        for attr_id_str in custom_attr_filters:
            attr_id = _parse_custom_attribute_id(attr_id_str)
            if attr_id:
                annotation_name = _get_annotation_field_name(attr_id)
                if annotation_name not in queryset.query.annotations:
                    attrs_to_annotate.append(attr_id_str)
        if attrs_to_annotate:
            logger.debug(
                "Annotating custom attributes for filtering",
                extra={
                    "num_annotations": len(attrs_to_annotate),
                },
            )
            queryset = annotate_custom_attributes(queryset, attrs_to_annotate, organization, content_type)

        combined_q = Q()
        for attr_id_str, filter_config in custom_attr_filters.items():
            attr_id = _parse_custom_attribute_id(attr_id_str)
            if not attr_id:
                logger.warning(
                    "Invalid attribute UUID in filter",
                    extra={"attribute_id_str": attr_id_str},
                )
                continue

            filter_q = _build_custom_attribute_filter(attr_id, filter_config, organization, content_type, queryset)
            if filter_q:
                combined_q &= filter_q

        if combined_q:
            queryset = queryset.filter(combined_q)
            logger.info(
                "Applied custom attribute filters",
                extra={
                    "organization_id": organization.id,
                    "num_filters": len(custom_attr_filters),
                },
            )

    if model_field_filters:
        model_q = Q(**model_field_filters)
        queryset = queryset.filter(model_q)
        logger.info(
            "Applied model field filters",
            extra={
                "organization_id": organization.id,
                "num_filters": len(model_field_filters),
            },
        )

    return queryset
