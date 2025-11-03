"""Service for managing list view preferences."""

import logging
from datetime import date
from typing import Any
from uuid import UUID

from django.contrib.contenttypes.models import ContentType
from django.http import HttpRequest
from guardian.shortcuts import assign_perm

from sandwich.core.models import CustomAttribute
from sandwich.core.models import CustomAttributeEnum
from sandwich.core.models import ListViewPreference
from sandwich.core.models import ListViewType
from sandwich.core.models import Organization
from sandwich.core.models import PreferenceScope
from sandwich.core.models.encounter import Encounter
from sandwich.core.models.patient import Patient
from sandwich.core.models.role import RoleName
from sandwich.users.models import User

logger = logging.getLogger(__name__)

DEFAULT_ITEMS_PER_PAGE = 25
DEFAULT_SORT = "-updated_at"


def validate_list_type(
    list_type: str,
    *,
    user_id: int | None = None,
    organization_id: UUID | None = None,
) -> ListViewType:
    try:
        return ListViewType(list_type)
    except ValueError:
        log_extra: dict[str, Any] = {"list_type": list_type}
        if user_id:
            log_extra["user_id"] = user_id
        if organization_id:
            log_extra["organization_id"] = organization_id

        logger.warning(
            "Invalid list type",
            extra=log_extra,
        )
        raise


def assign_default_listviewpreference_perms(preference: ListViewPreference) -> None:
    """
    Assign default permissions for a ListViewPreference.

    Organization-level preferences get permissions for owner, admin, and staff roles.
    User-level preferences get permissions for the owning user only.
    """
    if preference.scope == PreferenceScope.ORGANIZATION:
        # Organization-level preferences: assign to owner, admin, staff roles
        roles = preference.organization.role_set.exclude(name=RoleName.PATIENT)
        for role in roles:
            assign_perm("view_listviewpreference", role.group, preference)
            # Only owners and admins can change org-level preferences
            if role.name in [RoleName.OWNER, RoleName.ADMIN]:
                assign_perm("change_listviewpreference", role.group, preference)
                assign_perm("delete_listviewpreference", role.group, preference)

    elif preference.scope == PreferenceScope.USER and preference.user:
        # User-level preferences: assign to the owning user
        assign_perm("view_listviewpreference", preference.user, preference)
        assign_perm("change_listviewpreference", preference.user, preference)
        assign_perm("delete_listviewpreference", preference.user, preference)


def _fill_missing_defaults(preference: ListViewPreference, list_type: ListViewType) -> None:
    """Fill in missing fields with hardcoded defaults."""
    if not preference.default_sort:
        preference.default_sort = get_default_sort(list_type)
    if not preference.visible_columns:
        preference.visible_columns = get_default_columns(list_type)


def _create_default_preference(
    user: User,
    organization: Organization,
    list_type: ListViewType,
) -> ListViewPreference:
    """
    Create an unsaved ListViewPreference instance with hardcoded defaults.

    This is used as a fallback when no saved preference exists.
    """
    return ListViewPreference(
        user=None,
        organization=organization,
        list_type=list_type,
        scope=PreferenceScope.ORGANIZATION,
        visible_columns=get_default_columns(list_type),
        default_sort=get_default_sort(list_type),
        saved_filters={},
        items_per_page=DEFAULT_ITEMS_PER_PAGE,
    )


def get_list_view_preference(
    user: User,
    organization: Organization,
    list_type: ListViewType,
) -> ListViewPreference:
    """
    Get the effective list preference for a user in an organization.

    Priority:
    1. User's personal preference (if exists)
    2. Organization default preference (if exists)
    3. Unsaved preference object with hardcoded defaults

    Always returns a ListViewPreference with all fields populated.
    If a preference is found but has missing values (empty default_sort or visible_columns),
    those fields will be populated with hardcoded defaults.
    """
    logger.debug(
        "Fetching list preference",
        extra={
            "user_id": user.id,
            "organization_id": organization.id,
            "list_type": list_type,
        },
    )

    user_pref = (
        ListViewPreference.objects.filter(
            user=user,
            organization=organization,
            list_type=list_type,
            scope=PreferenceScope.USER,
        )
        .select_related("user", "organization")
        .first()
    )

    if user_pref:
        logger.debug(
            "Found user preference",
            extra={
                "user_id": user.id,
                "preference_id": user_pref.id,
            },
        )
        return user_pref

    org_pref = (
        ListViewPreference.objects.filter(
            organization=organization,
            list_type=list_type,
            scope=PreferenceScope.ORGANIZATION,
            user__isnull=True,
        )
        .select_related("organization")
        .first()
    )

    if org_pref:
        logger.debug(
            "Using organization default preference",
            extra={
                "organization_id": organization.id,
                "preference_id": org_pref.id,
            },
        )
        return org_pref

    # No saved preference exists, return unsaved default
    logger.debug(
        "Using hardcoded defaults (no saved preference)",
        extra={
            "user_id": user.id,
            "organization_id": organization.id,
            "list_type": list_type,
        },
    )
    return _create_default_preference(user, organization, list_type)


def save_list_view_preference(  # noqa: PLR0913
    organization: Organization,
    list_type: ListViewType,
    *,
    user: User | None = None,
    visible_columns: list[str] | None = None,
    default_sort: str | None = None,
    saved_filters: dict[str, Any] | None = None,
    items_per_page: int | None = None,
) -> ListViewPreference:
    """
    Save or update a list preference.

    If user is provided, saves a user-level preference.
    If user is None, saves an organization-level default preference.
    """
    scope = PreferenceScope.USER if user else PreferenceScope.ORGANIZATION

    log_extra: dict[str, Any] = {
        "organization_id": organization.id,
        "list_type": list_type,
        "scope": scope.value,
    }
    if user:
        log_extra["user_id"] = user.id

    logger.info(
        "Saving list preference",
        extra=log_extra,
    )

    filter_kwargs: dict[str, Any] = {
        "organization": organization,
        "list_type": list_type,
        "scope": scope,
    }
    if user:
        filter_kwargs["user"] = user
    else:
        filter_kwargs["user__isnull"] = True

    pref, created = ListViewPreference.objects.update_or_create(
        **filter_kwargs,
        defaults={
            "visible_columns": visible_columns or [],
            "default_sort": default_sort or "",
            "saved_filters": saved_filters or {},
            "items_per_page": items_per_page or 25,
        },
    )

    # Assign permissions for newly created preferences
    if created:
        assign_default_listviewpreference_perms(pref)

    action = "created" if created else "updated"
    log_extra["preference_id"] = pref.id
    log_extra["action"] = action
    logger.info(
        "List preference %s",
        action,
        extra=log_extra,
    )

    return pref


def reset_list_view_preference(
    organization: Organization,
    list_type: ListViewType,
    *,
    user: User | None = None,
) -> None:
    """
    Reset a list preference, causing fallback to defaults.

    If user is provided, resets the user's personal preference (falls back to org or system defaults).
    If user is None, resets the organization's default preference (falls back to system defaults).
    """
    scope = PreferenceScope.USER if user else PreferenceScope.ORGANIZATION

    log_extra: dict[str, Any] = {
        "organization_id": organization.id,
        "list_type": list_type,
        "scope": scope.value,
    }
    if user:
        log_extra["user_id"] = user.id

    logger.info(
        "Resetting list preference",
        extra=log_extra,
    )

    filter_kwargs: dict[str, Any] = {
        "organization": organization,
        "list_type": list_type,
        "scope": scope,
    }
    if user:
        filter_kwargs["user"] = user
    else:
        filter_kwargs["user__isnull"] = True

    ListViewPreference.objects.filter(**filter_kwargs).delete()


def get_default_columns(list_type: ListViewType) -> list[str]:
    """Get hardcoded default columns for a list type."""
    defaults = {
        ListViewType.ENCOUNTER_LIST: [
            "patient__first_name",
            "patient__email",
            "active",
            "created_at",
            "updated_at",
        ],
        ListViewType.PATIENT_LIST: [
            "first_name",
            "email",
            "has_active_encounter",
            "created_at",
            "updated_at",
        ],
    }
    return defaults.get(list_type, [])


def get_default_sort(list_type: ListViewType) -> str:
    """Get hardcoded default sort for a list type."""
    defaults = {
        ListViewType.ENCOUNTER_LIST: DEFAULT_SORT,
        ListViewType.PATIENT_LIST: DEFAULT_SORT,
    }
    return defaults.get(list_type, DEFAULT_SORT)


def _get_list_type_content_type(list_type: ListViewType) -> ContentType | None:
    """Map list type to the corresponding Django ContentType."""
    content_type_map = {
        ListViewType.ENCOUNTER_LIST: ContentType.objects.get_for_model(Encounter),
        ListViewType.PATIENT_LIST: ContentType.objects.get_for_model(Patient),
    }
    return content_type_map.get(list_type)


def _get_custom_attribute_columns(
    list_type: ListViewType,
    organization: Organization,
) -> list[dict[str, str]]:
    """
    Get custom attribute columns for a list type within an organization.

    Custom attribute columns use the UUID as the value.
    """
    content_type = _get_list_type_content_type(list_type)
    if not content_type:
        return []

    custom_attributes = CustomAttribute.objects.filter(
        organization=organization,
        content_type=content_type,
    ).order_by("name")

    columns = [
        {
            "value": str(attr.id),
            "label": attr.name,
            "data_type": attr.data_type,
            "is_custom": "true",
        }
        for attr in custom_attributes
    ]

    logger.debug(
        "Found custom attribute columns",
        extra={
            "list_type": list_type,
            "organization_id": organization.id,
            "count": len(columns),
        },
    )

    return columns


def validate_sort_field(
    sort_field: str,
    list_type: ListViewType,
    organization: Organization,
) -> bool:
    """Validate that a sort field is valid for the given list type and organization."""
    # Strip leading '-' for descending sorts
    field = sort_field.lstrip("-")

    available_columns = get_available_columns(list_type, organization)
    available_values = {col["value"] for col in available_columns}

    return field in available_values


def get_available_columns(
    list_type: ListViewType,
    organization: Organization | None = None,
) -> list[dict[str, str]]:
    """
    Get all available columns for a list type with their labels.

    If organization is provided, includes custom attributes.
    """
    columns = {
        ListViewType.ENCOUNTER_LIST: [
            {"value": "patient__first_name", "label": "Patient Name"},
            {"value": "patient__email", "label": "Email"},
            {"value": "patient__date_of_birth", "label": "Date of Birth"},
            {"value": "active", "label": "Active/Archived"},
            {"value": "created_at", "label": "Created"},
            {"value": "updated_at", "label": "Last Updated"},
        ],
        ListViewType.PATIENT_LIST: [
            {"value": "first_name", "label": "Name"},
            {"value": "email", "label": "Email"},
            {"value": "date_of_birth", "label": "Date of Birth"},
            {"value": "has_active_encounter", "label": "Active Encounter"},
            {"value": "created_at", "label": "Created"},
            {"value": "updated_at", "label": "Last Updated"},
        ],
    }
    base_columns = columns.get(list_type, [])

    # Add custom attribute columns if organization provided
    if organization:
        custom_columns = _get_custom_attribute_columns(list_type, organization)
        return base_columns + custom_columns

    return base_columns


def _validate_enum_filter_values(
    attribute: CustomAttribute,
    filter_config: dict[str, Any],
) -> dict[str, str]:
    """Validate enum filter values against the attribute's allowed enum values."""
    errors = {}
    values = filter_config.get("values", [])

    if not isinstance(values, list):
        errors["values"] = "Enum filter values must be a list"
    elif values:
        valid_values = set(
            CustomAttributeEnum.objects.filter(attribute=attribute, value__in=values).values_list("value", flat=True)
        )
        invalid_values = [v for v in values if v not in valid_values]
        if invalid_values:
            errors["values"] = f"Invalid enum values: {', '.join(invalid_values)}"

    return errors


def _validate_date_value(value: Any, field_name: str = "value") -> dict[str, str]:
    """Validate a single date value, returning errors if invalid."""
    errors = {}
    if value:
        try:
            date.fromisoformat(value) if isinstance(value, str) else value
        except (ValueError, TypeError):
            errors[field_name] = f"Invalid date format for {field_name}"
    return errors


def _validate_date_range(start: Any, end: Any) -> dict[str, str]:
    """Validate date range values, checking format and logical ordering."""
    errors = {}

    if start:
        errors.update(_validate_date_value(start, "start"))

    if end:
        errors.update(_validate_date_value(end, "end"))

    # Only check range logic if both dates are valid
    if not errors and start and end:
        start_date = date.fromisoformat(start) if isinstance(start, str) else start
        end_date = date.fromisoformat(end) if isinstance(end, str) else end
        if start_date > end_date:
            errors["range"] = "Start date must be before or equal to end date"

    return errors


def _validate_date_filter(filter_config: dict[str, Any]) -> dict[str, str]:
    """Validate date filter configuration based on operator type."""
    errors = {}
    operator = filter_config.get("operator", "exact")

    if operator not in ("exact", "gte", "lte", "range"):
        errors["operator"] = f"Invalid date operator: {operator}"
        return errors

    if operator == "range":
        start = filter_config.get("start")
        end = filter_config.get("end")
        errors.update(_validate_date_range(start, end))
    else:
        value = filter_config.get("value")
        errors.update(_validate_date_value(value))

    return errors


def validate_custom_attribute_filter(
    attribute_id: UUID,
    filter_config: dict[str, Any],
    organization: Organization,
    content_type: ContentType,
) -> dict[str, str]:
    """Validate a custom attribute filter configuration, returning dict of errors (empty if valid)."""
    errors = {}

    try:
        attribute = CustomAttribute.objects.get(id=attribute_id, organization=organization)
    except CustomAttribute.DoesNotExist:
        errors["attribute"] = f"Custom attribute {attribute_id} not found in organization"
        return errors

    if attribute.content_type_id != content_type.id:
        errors["content_type"] = (
            f"Attribute content_type ({attribute.content_type.model}) does not match expected ({content_type.model})"
        )
        return errors

    if attribute.data_type == CustomAttribute.DataType.ENUM:
        errors.update(_validate_enum_filter_values(attribute, filter_config))
    elif attribute.data_type == CustomAttribute.DataType.DATE:
        errors.update(_validate_date_filter(filter_config))

    logger.debug(
        "Validated custom attribute filter",
        extra={
            "attribute_id": str(attribute_id),
            "is_valid": len(errors) == 0,
            "errors": errors,
        },
    )

    return errors


def _parse_filter_key(key: str) -> tuple[str, str | None]:
    """
    Parse a filter key to extract UUID part and optional suffix.

    Returns:
        Tuple of (uuid_part, suffix) where suffix is 'start', 'end', or None
    """
    remainder = key[len("filter_attr_") :]

    if remainder.endswith("_start"):
        return remainder[: -len("_start")], "start"
    if remainder.endswith("_end"):
        return remainder[: -len("_end")], "end"
    return remainder, None


def _parse_attribute_uuid(uuid_part: str) -> UUID | None:
    """Parse UUID from filter key, returning None if invalid."""
    try:
        return UUID(uuid_part.replace("_", "-"))
    except (ValueError, AttributeError):
        return None


def _apply_range_filter(
    filters: dict[str, Any],
    attr_id_str: str,
    suffix: str,
    value: str | None,
) -> None:
    """Apply a range filter (start or end) to the filters dictionary."""
    if attr_id_str not in filters["custom_attributes"]:
        filters["custom_attributes"][attr_id_str] = {}

    filters["custom_attributes"][attr_id_str]["operator"] = "range"
    filters["custom_attributes"][attr_id_str][suffix] = value


def _apply_values_filter(
    filters: dict[str, Any],
    attr_id_str: str,
    value: str,
) -> None:
    """Apply a comma-separated values filter to the filters dictionary."""
    values = [v.strip() for v in value.split(",") if v.strip()]
    if values:
        if attr_id_str not in filters["custom_attributes"]:
            filters["custom_attributes"][attr_id_str] = {}
        filters["custom_attributes"][attr_id_str]["values"] = values


def _process_custom_attribute_filter(
    key: str,
    request: HttpRequest,
    filters: dict[str, Any],
) -> None:
    """Process a single custom attribute filter from request parameters."""
    uuid_part, suffix = _parse_filter_key(key)
    attr_id = _parse_attribute_uuid(uuid_part)

    if attr_id is None:
        logger.warning(
            "Invalid attribute UUID in request filter",
            extra={"key": key, "uuid_part": uuid_part},
        )
        return

    attr_id_str = str(attr_id)
    value = request.GET.get(key)

    if suffix in ("start", "end"):
        _apply_range_filter(filters, attr_id_str, suffix, value)
    elif value:
        _apply_values_filter(filters, attr_id_str, value)


def parse_filters_from_request(
    request: HttpRequest,
    preference: ListViewPreference,
) -> dict[str, Any]:
    """Extract and merge filters from request and saved preference (request params override saved)."""
    filters = preference.saved_filters.copy() if preference.saved_filters else {}

    if "custom_attributes" not in filters:
        filters["custom_attributes"] = {}
    if "model_fields" not in filters:
        filters["model_fields"] = {}

    for key in request.GET:
        if key.startswith("filter_attr_"):
            _process_custom_attribute_filter(key, request, filters)

    logger.debug(
        "Parsed filters from request",
        extra={
            "num_custom_filters": len(filters.get("custom_attributes", {})),
            "num_model_filters": len(filters.get("model_fields", {})),
            "has_request_overrides": any(key.startswith("filter_") for key in request.GET),
        },
    )

    return filters


def _validate_and_clean_custom_attribute_filters(
    filters: dict[str, Any],
    organization: Organization,
    content_type: ContentType,
) -> None:
    """
    Validate custom attribute filters and remove invalid ones in-place.

    Modifies the filters dictionary by removing filters with invalid UUIDs or validation errors.
    """
    custom_attr_filters = filters.get("custom_attributes", {})
    invalid_keys = []

    for attr_id_str, filter_config in custom_attr_filters.items():
        try:
            attr_id = UUID(attr_id_str)
            errors = validate_custom_attribute_filter(attr_id, filter_config, organization, content_type)
            if errors:
                logger.warning(
                    "Invalid filter not saved",
                    extra={
                        "attribute_id": attr_id_str,
                        "errors": errors,
                    },
                )
                invalid_keys.append(attr_id_str)
        except (ValueError, AttributeError):
            logger.warning(
                "Invalid attribute UUID, removing filter",
                extra={"attribute_id_str": attr_id_str},
            )
            invalid_keys.append(attr_id_str)

    for key in invalid_keys:
        del filters["custom_attributes"][key]


def save_filters_to_preference(
    preference: ListViewPreference,
    filters: dict[str, Any],
) -> ListViewPreference:
    """Save filters to a ListViewPreference instance, validating before saving."""
    organization = preference.organization
    list_type = ListViewType(preference.list_type)
    content_type = _get_list_type_content_type(list_type)

    if content_type:
        _validate_and_clean_custom_attribute_filters(filters, organization, content_type)

    preference.saved_filters = filters

    if preference.pk:
        preference.save(update_fields=["saved_filters", "updated_at"])
        logger.info(
            "Saved filters to preference",
            extra={
                "preference_id": preference.pk,
                "num_custom_filters": len(filters.get("custom_attributes", {})),
            },
        )
    else:
        logger.debug("Filters updated on unsaved preference instance")

    return preference
