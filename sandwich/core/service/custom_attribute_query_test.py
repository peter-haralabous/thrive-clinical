from datetime import date
from uuid import UUID

import pytest
from django.contrib.contenttypes.models import ContentType

from sandwich.core.factories.organization import OrganizationFactory
from sandwich.core.factories.patient import PatientFactory
from sandwich.core.models import CustomAttribute
from sandwich.core.models import CustomAttributeEnum
from sandwich.core.models import CustomAttributeValue
from sandwich.core.models.encounter import Encounter
from sandwich.core.models.encounter import EncounterStatus
from sandwich.core.service.custom_attribute_query import _get_annotation_field_name
from sandwich.core.service.custom_attribute_query import _parse_custom_attribute_id
from sandwich.core.service.custom_attribute_query import annotate_custom_attributes
from sandwich.core.service.custom_attribute_query import apply_filters_with_custom_attributes
from sandwich.core.service.custom_attribute_query import apply_sort_with_custom_attributes


@pytest.mark.django_db
class TestCustomAttributeQueryHelpers:
    def test_get_annotation_field_name(self):
        attr_id = UUID("550e8400-e29b-41d4-a716-446655440000")
        field_name = _get_annotation_field_name(attr_id)

        assert field_name == "attr_550e8400_e29b_41d4_a716_446655440000"
        assert "-" not in field_name

    def test_parse_custom_attribute_id_valid(self):
        column = "550e8400-e29b-41d4-a716-446655440000"
        attr_id = _parse_custom_attribute_id(column)

        assert attr_id is not None
        assert str(attr_id) == "550e8400-e29b-41d4-a716-446655440000"

    def test_parse_custom_attribute_id_invalid(self):
        assert _parse_custom_attribute_id("patient__first_name") is None
        assert _parse_custom_attribute_id("invalid_uuid") is None
        assert _parse_custom_attribute_id("") is None


@pytest.mark.django_db
class TestAnnotateCustomAttributes:
    def test_annotate_multiple_attributes(self):
        org = OrganizationFactory.create()
        patient = PatientFactory.create(organization=org)
        encounter = Encounter.objects.create(
            organization=org,
            patient=patient,
            status=EncounterStatus.IN_PROGRESS,
        )

        content_type = ContentType.objects.get_for_model(Encounter)

        priority_attr = CustomAttribute.objects.create(
            organization=org,
            content_type=content_type,
            name="Priority",
            data_type=CustomAttribute.DataType.ENUM,
        )
        high_priority = CustomAttributeEnum.objects.create(
            attribute=priority_attr,
            label="High",
            value="high",
        )
        CustomAttributeValue.objects.create(
            attribute=priority_attr,
            content_type=content_type,
            object_id=encounter.id,
            value_enum=high_priority,
        )

        followup_attr = CustomAttribute.objects.create(
            organization=org,
            content_type=content_type,
            name="Follow-up Date",
            data_type=CustomAttribute.DataType.DATE,
        )
        CustomAttributeValue.objects.create(
            attribute=followup_attr,
            content_type=content_type,
            object_id=encounter.id,
            value_date=date(2025, 12, 31),
        )

        encounters = Encounter.objects.filter(id=encounter.id)
        annotated = annotate_custom_attributes(
            encounters,
            [str(priority_attr.id), str(followup_attr.id)],
            org,
            content_type,
        )

        result = annotated.first()
        assert result is not None

        priority_annotation = _get_annotation_field_name(priority_attr.id)
        followup_annotation = _get_annotation_field_name(followup_attr.id)

        assert hasattr(result, priority_annotation)
        assert hasattr(result, followup_annotation)
        assert getattr(result, priority_annotation) == "High"
        assert getattr(result, followup_annotation) == date(2025, 12, 31)

    def test_annotate_no_custom_columns(self):
        org = OrganizationFactory.create()
        content_type = ContentType.objects.get_for_model(Encounter)

        encounters = Encounter.objects.all()
        annotated = annotate_custom_attributes(
            encounters,
            ["patient__first_name", "created_at"],  # No custom attributes
            org,
            content_type,
        )

        assert list(encounters) == list(annotated)

    def test_annotate_handles_missing_values(self):
        org = OrganizationFactory.create()
        patient = PatientFactory.create(organization=org)
        encounter = Encounter.objects.create(
            organization=org,
            patient=patient,
            status=EncounterStatus.IN_PROGRESS,
        )

        content_type = ContentType.objects.get_for_model(Encounter)

        # Create custom attribute but don't set a value
        priority_attr = CustomAttribute.objects.create(
            organization=org,
            content_type=content_type,
            name="Priority",
            data_type=CustomAttribute.DataType.ENUM,
        )

        # Annotate queryset
        encounters = Encounter.objects.filter(id=encounter.id)
        annotated = annotate_custom_attributes(
            encounters,
            [str(priority_attr.id)],
            org,
            content_type,
        )

        result = annotated.first()
        assert result is not None

        annotation_name = _get_annotation_field_name(priority_attr.id)
        assert hasattr(result, annotation_name)
        assert getattr(result, annotation_name) is None


@pytest.mark.django_db
class TestApplySortWithCustomAttributes:
    def test_sort_by_enum_attribute_ascending(self):
        org = OrganizationFactory.create()
        patient = PatientFactory.create(organization=org)

        content_type = ContentType.objects.get_for_model(Encounter)

        priority_attr = CustomAttribute.objects.create(
            organization=org,
            content_type=content_type,
            name="Priority",
            data_type=CustomAttribute.DataType.ENUM,
        )

        high = CustomAttributeEnum.objects.create(attribute=priority_attr, label="High", value="high")
        low = CustomAttributeEnum.objects.create(attribute=priority_attr, label="Low", value="low")

        encounter1 = Encounter.objects.create(organization=org, patient=patient, status=EncounterStatus.IN_PROGRESS)
        encounter2 = Encounter.objects.create(organization=org, patient=patient, status=EncounterStatus.IN_PROGRESS)

        CustomAttributeValue.objects.create(
            attribute=priority_attr,
            content_type=content_type,
            object_id=encounter1.id,
            value_enum=low,
        )
        CustomAttributeValue.objects.create(
            attribute=priority_attr,
            content_type=content_type,
            object_id=encounter2.id,
            value_enum=high,
        )

        encounters = Encounter.objects.filter(organization=org)
        sorted_encounters = apply_sort_with_custom_attributes(
            encounters,
            str(priority_attr.id),  # Ascending
            org,
            content_type,
        )

        results = list(sorted_encounters)
        assert len(results) == 2
        # High comes before Low alphabetically
        annotation_name = _get_annotation_field_name(priority_attr.id)
        assert getattr(results[0], annotation_name) == "High"
        assert getattr(results[1], annotation_name) == "Low"

    def test_sort_by_enum_attribute_descending(self):
        org = OrganizationFactory.create()
        patient = PatientFactory.create(organization=org)

        content_type = ContentType.objects.get_for_model(Encounter)

        priority_attr = CustomAttribute.objects.create(
            organization=org,
            content_type=content_type,
            name="Priority",
            data_type=CustomAttribute.DataType.ENUM,
        )

        high = CustomAttributeEnum.objects.create(attribute=priority_attr, label="High", value="high")
        low = CustomAttributeEnum.objects.create(attribute=priority_attr, label="Low", value="low")

        encounter1 = Encounter.objects.create(organization=org, patient=patient, status=EncounterStatus.IN_PROGRESS)
        encounter2 = Encounter.objects.create(organization=org, patient=patient, status=EncounterStatus.IN_PROGRESS)

        CustomAttributeValue.objects.create(
            attribute=priority_attr,
            content_type=content_type,
            object_id=encounter1.id,
            value_enum=low,
        )
        CustomAttributeValue.objects.create(
            attribute=priority_attr,
            content_type=content_type,
            object_id=encounter2.id,
            value_enum=high,
        )

        encounters = Encounter.objects.filter(organization=org)
        sorted_encounters = apply_sort_with_custom_attributes(
            encounters,
            f"-{priority_attr.id}",
            org,
            content_type,
        )

        results = list(sorted_encounters)
        assert len(results) == 2
        annotation_name = _get_annotation_field_name(priority_attr.id)
        assert getattr(results[0], annotation_name) == "Low"
        assert getattr(results[1], annotation_name) == "High"

    def test_sort_by_model_field(self):
        org = OrganizationFactory.create()
        patient = PatientFactory.create(organization=org)

        Encounter.objects.create(organization=org, patient=patient, status=EncounterStatus.IN_PROGRESS)
        Encounter.objects.create(organization=org, patient=patient, status=EncounterStatus.IN_PROGRESS)

        content_type = ContentType.objects.get_for_model(Encounter)

        encounters = Encounter.objects.filter(organization=org)
        sorted_encounters = apply_sort_with_custom_attributes(
            encounters,
            "-created_at",  # Standard field
            org,
            content_type,
        )

        results = list(sorted_encounters)
        assert len(results) == 2
        assert results[0].created_at >= results[1].created_at


@pytest.mark.django_db
class TestApplyFiltersWithCustomAttributes:
    def test_filter_by_single_enum_attribute(self):
        org = OrganizationFactory.create()
        patient = PatientFactory.create(organization=org)
        content_type = ContentType.objects.get_for_model(Encounter)

        priority_attr = CustomAttribute.objects.create(
            organization=org,
            content_type=content_type,
            name="Priority",
            data_type=CustomAttribute.DataType.ENUM,
        )
        high = CustomAttributeEnum.objects.create(attribute=priority_attr, label="High", value="high")
        low = CustomAttributeEnum.objects.create(attribute=priority_attr, label="Low", value="low")

        encounter1 = Encounter.objects.create(organization=org, patient=patient, status=EncounterStatus.IN_PROGRESS)
        encounter2 = Encounter.objects.create(organization=org, patient=patient, status=EncounterStatus.IN_PROGRESS)
        Encounter.objects.create(organization=org, patient=patient, status=EncounterStatus.IN_PROGRESS)

        CustomAttributeValue.objects.create(
            attribute=priority_attr,
            content_type=content_type,
            object_id=encounter1.id,
            value_enum=high,
        )
        CustomAttributeValue.objects.create(
            attribute=priority_attr,
            content_type=content_type,
            object_id=encounter2.id,
            value_enum=low,
        )

        encounters = Encounter.objects.filter(organization=org)
        filters = {
            "custom_attributes": {
                str(priority_attr.id): {
                    "type": "enum",
                    "values": ["high"],
                }
            }
        }

        filtered = apply_filters_with_custom_attributes(encounters, filters, org, content_type)
        results = list(filtered)

        assert len(results) == 1
        assert results[0].id == encounter1.id

    def test_filter_by_multi_value_enum_attribute(self):
        org = OrganizationFactory.create()
        patient = PatientFactory.create(organization=org)
        content_type = ContentType.objects.get_for_model(Encounter)

        tags_attr = CustomAttribute.objects.create(
            organization=org,
            content_type=content_type,
            name="Tags",
            data_type=CustomAttribute.DataType.ENUM,
            is_multi=True,
        )
        urgent = CustomAttributeEnum.objects.create(attribute=tags_attr, label="Urgent", value="urgent")
        followup = CustomAttributeEnum.objects.create(attribute=tags_attr, label="Follow-up", value="followup")
        routine = CustomAttributeEnum.objects.create(attribute=tags_attr, label="Routine", value="routine")

        encounter1 = Encounter.objects.create(organization=org, patient=patient, status=EncounterStatus.IN_PROGRESS)
        encounter2 = Encounter.objects.create(organization=org, patient=patient, status=EncounterStatus.IN_PROGRESS)
        Encounter.objects.create(organization=org, patient=patient, status=EncounterStatus.IN_PROGRESS)

        # encounter1: urgent, followup
        CustomAttributeValue.objects.create(
            attribute=tags_attr, content_type=content_type, object_id=encounter1.id, value_enum=urgent
        )
        CustomAttributeValue.objects.create(
            attribute=tags_attr, content_type=content_type, object_id=encounter1.id, value_enum=followup
        )

        # encounter2: routine
        CustomAttributeValue.objects.create(
            attribute=tags_attr, content_type=content_type, object_id=encounter2.id, value_enum=routine
        )

        encounters = Encounter.objects.filter(organization=org)
        filters = {
            "custom_attributes": {
                str(tags_attr.id): {
                    "type": "enum",
                    "values": ["urgent", "followup"],
                }
            }
        }

        filtered = apply_filters_with_custom_attributes(encounters, filters, org, content_type)
        results = list(filtered)

        # Should match encounter1 (has urgent or followup)
        assert len(results) == 1
        assert results[0].id == encounter1.id

    def test_filter_by_date_range(self):
        org = OrganizationFactory.create()
        patient = PatientFactory.create(organization=org)
        content_type = ContentType.objects.get_for_model(Encounter)

        followup_attr = CustomAttribute.objects.create(
            organization=org,
            content_type=content_type,
            name="Follow-up Date",
            data_type=CustomAttribute.DataType.DATE,
        )

        encounter1 = Encounter.objects.create(organization=org, patient=patient, status=EncounterStatus.IN_PROGRESS)
        encounter2 = Encounter.objects.create(organization=org, patient=patient, status=EncounterStatus.IN_PROGRESS)
        encounter3 = Encounter.objects.create(organization=org, patient=patient, status=EncounterStatus.IN_PROGRESS)

        CustomAttributeValue.objects.create(
            attribute=followup_attr,
            content_type=content_type,
            object_id=encounter1.id,
            value_date=date(2024, 1, 15),
        )
        CustomAttributeValue.objects.create(
            attribute=followup_attr,
            content_type=content_type,
            object_id=encounter2.id,
            value_date=date(2024, 6, 15),
        )
        CustomAttributeValue.objects.create(
            attribute=followup_attr,
            content_type=content_type,
            object_id=encounter3.id,
            value_date=date(2024, 12, 15),
        )

        encounters = Encounter.objects.filter(organization=org)
        filters = {
            "custom_attributes": {
                str(followup_attr.id): {
                    "type": "date",
                    "operator": "range",
                    "start": "2024-05-01",
                    "end": "2024-10-31",
                }
            }
        }

        filtered = apply_filters_with_custom_attributes(encounters, filters, org, content_type)
        results = list(filtered)

        assert len(results) == 1
        assert results[0].id == encounter2.id

    def test_filter_by_date_exact(self):
        org = OrganizationFactory.create()
        patient = PatientFactory.create(organization=org)
        content_type = ContentType.objects.get_for_model(Encounter)

        followup_attr = CustomAttribute.objects.create(
            organization=org,
            content_type=content_type,
            name="Follow-up Date",
            data_type=CustomAttribute.DataType.DATE,
        )

        encounter1 = Encounter.objects.create(organization=org, patient=patient, status=EncounterStatus.IN_PROGRESS)
        encounter2 = Encounter.objects.create(organization=org, patient=patient, status=EncounterStatus.IN_PROGRESS)

        target_date = date(2024, 6, 15)
        CustomAttributeValue.objects.create(
            attribute=followup_attr,
            content_type=content_type,
            object_id=encounter1.id,
            value_date=target_date,
        )
        CustomAttributeValue.objects.create(
            attribute=followup_attr,
            content_type=content_type,
            object_id=encounter2.id,
            value_date=date(2024, 7, 15),
        )

        encounters = Encounter.objects.filter(organization=org)
        filters = {
            "custom_attributes": {
                str(followup_attr.id): {
                    "type": "date",
                    "operator": "exact",
                    "value": "2024-06-15",
                }
            }
        }

        filtered = apply_filters_with_custom_attributes(encounters, filters, org, content_type)
        results = list(filtered)

        assert len(results) == 1
        assert results[0].id == encounter1.id

    def test_multiple_filters_combined(self):
        org = OrganizationFactory.create()
        patient = PatientFactory.create(organization=org)
        content_type = ContentType.objects.get_for_model(Encounter)

        priority_attr = CustomAttribute.objects.create(
            organization=org,
            content_type=content_type,
            name="Priority",
            data_type=CustomAttribute.DataType.ENUM,
        )
        high = CustomAttributeEnum.objects.create(attribute=priority_attr, label="High", value="high")
        low = CustomAttributeEnum.objects.create(attribute=priority_attr, label="Low", value="low")

        followup_attr = CustomAttribute.objects.create(
            organization=org,
            content_type=content_type,
            name="Follow-up Date",
            data_type=CustomAttribute.DataType.DATE,
        )

        encounter1 = Encounter.objects.create(organization=org, patient=patient, status=EncounterStatus.IN_PROGRESS)
        encounter2 = Encounter.objects.create(organization=org, patient=patient, status=EncounterStatus.IN_PROGRESS)
        encounter3 = Encounter.objects.create(organization=org, patient=patient, status=EncounterStatus.IN_PROGRESS)

        # encounter1: high priority, date in June
        CustomAttributeValue.objects.create(
            attribute=priority_attr, content_type=content_type, object_id=encounter1.id, value_enum=high
        )
        CustomAttributeValue.objects.create(
            attribute=followup_attr, content_type=content_type, object_id=encounter1.id, value_date=date(2024, 6, 15)
        )

        # encounter2: high priority, date in December
        CustomAttributeValue.objects.create(
            attribute=priority_attr, content_type=content_type, object_id=encounter2.id, value_enum=high
        )
        CustomAttributeValue.objects.create(
            attribute=followup_attr, content_type=content_type, object_id=encounter2.id, value_date=date(2024, 12, 15)
        )

        # encounter3: low priority, date in June
        CustomAttributeValue.objects.create(
            attribute=priority_attr, content_type=content_type, object_id=encounter3.id, value_enum=low
        )
        CustomAttributeValue.objects.create(
            attribute=followup_attr, content_type=content_type, object_id=encounter3.id, value_date=date(2024, 6, 20)
        )

        encounters = Encounter.objects.filter(organization=org)
        filters = {
            "custom_attributes": {
                str(priority_attr.id): {
                    "type": "enum",
                    "values": ["high"],
                },
                str(followup_attr.id): {
                    "type": "date",
                    "operator": "range",
                    "start": "2024-06-01",
                    "end": "2024-06-30",
                },
            }
        }

        filtered = apply_filters_with_custom_attributes(encounters, filters, org, content_type)
        results = list(filtered)

        # Should only match encounter1 (high priority AND June date)
        assert len(results) == 1
        assert results[0].id == encounter1.id

    def test_filter_with_null_values(self):
        org = OrganizationFactory.create()
        patient = PatientFactory.create(organization=org)
        content_type = ContentType.objects.get_for_model(Encounter)

        priority_attr = CustomAttribute.objects.create(
            organization=org,
            content_type=content_type,
            name="Priority",
            data_type=CustomAttribute.DataType.ENUM,
        )
        high = CustomAttributeEnum.objects.create(attribute=priority_attr, label="High", value="high")

        encounter1 = Encounter.objects.create(organization=org, patient=patient, status=EncounterStatus.IN_PROGRESS)
        Encounter.objects.create(organization=org, patient=patient, status=EncounterStatus.IN_PROGRESS)

        CustomAttributeValue.objects.create(
            attribute=priority_attr, content_type=content_type, object_id=encounter1.id, value_enum=high
        )

        encounters = Encounter.objects.filter(organization=org)
        filters = {
            "custom_attributes": {
                str(priority_attr.id): {
                    "type": "enum",
                    "values": ["high"],
                    "include_null": True,
                }
            }
        }

        filtered = apply_filters_with_custom_attributes(encounters, filters, org, content_type)
        results = list(filtered)

        # Should match both encounters (high priority OR null)
        assert len(results) == 2

    def test_filter_on_hidden_column_annotates_dynamically(self):
        org = OrganizationFactory.create()
        patient = PatientFactory.create(organization=org)
        content_type = ContentType.objects.get_for_model(Encounter)

        priority_attr = CustomAttribute.objects.create(
            organization=org,
            content_type=content_type,
            name="Priority",
            data_type=CustomAttribute.DataType.ENUM,
        )
        high = CustomAttributeEnum.objects.create(attribute=priority_attr, label="High", value="high")

        encounter = Encounter.objects.create(organization=org, patient=patient, status=EncounterStatus.IN_PROGRESS)
        CustomAttributeValue.objects.create(
            attribute=priority_attr, content_type=content_type, object_id=encounter.id, value_enum=high
        )

        encounters = Encounter.objects.filter(organization=org)
        assert not hasattr(encounters.first(), _get_annotation_field_name(priority_attr.id))

        filters = {
            "custom_attributes": {
                str(priority_attr.id): {
                    "type": "enum",
                    "values": ["high"],
                }
            }
        }

        filtered = apply_filters_with_custom_attributes(encounters, filters, org, content_type)
        results = list(filtered)

        assert len(results) == 1

    def test_filter_on_visible_column_reuses_annotation(self):
        org = OrganizationFactory.create()
        patient = PatientFactory.create(organization=org)
        content_type = ContentType.objects.get_for_model(Encounter)

        priority_attr = CustomAttribute.objects.create(
            organization=org,
            content_type=content_type,
            name="Priority",
            data_type=CustomAttribute.DataType.ENUM,
        )
        high = CustomAttributeEnum.objects.create(attribute=priority_attr, label="High", value="high")

        encounter = Encounter.objects.create(organization=org, patient=patient, status=EncounterStatus.IN_PROGRESS)
        CustomAttributeValue.objects.create(
            attribute=priority_attr, content_type=content_type, object_id=encounter.id, value_enum=high
        )

        encounters = Encounter.objects.filter(organization=org)
        encounters = annotate_custom_attributes(encounters, [str(priority_attr.id)], org, content_type)

        filters = {
            "custom_attributes": {
                str(priority_attr.id): {
                    "type": "enum",
                    "values": ["high"],
                }
            }
        }

        filtered = apply_filters_with_custom_attributes(encounters, filters, org, content_type)
        results = list(filtered)

        assert len(results) == 1

    def test_empty_filter_returns_unmodified_queryset(self):
        org = OrganizationFactory.create()
        patient = PatientFactory.create(organization=org)
        content_type = ContentType.objects.get_for_model(Encounter)

        Encounter.objects.create(organization=org, patient=patient, status=EncounterStatus.IN_PROGRESS)
        Encounter.objects.create(organization=org, patient=patient, status=EncounterStatus.IN_PROGRESS)

        encounters = Encounter.objects.filter(organization=org)
        filtered = apply_filters_with_custom_attributes(encounters, {}, org, content_type)

        assert list(encounters) == list(filtered)

    def test_invalid_attribute_uuid_skipped_with_warning(self):
        org = OrganizationFactory.create()
        patient = PatientFactory.create(organization=org)
        content_type = ContentType.objects.get_for_model(Encounter)

        encounter = Encounter.objects.create(organization=org, patient=patient, status=EncounterStatus.IN_PROGRESS)

        encounters = Encounter.objects.filter(organization=org)
        filters = {
            "custom_attributes": {
                "550e8400-e29b-41d4-a716-446655440000": {
                    "type": "enum",
                    "values": ["high"],
                }
            }
        }

        filtered = apply_filters_with_custom_attributes(encounters, filters, org, content_type)
        results = list(filtered)

        assert len(results) == 1
        assert results[0].id == encounter.id
