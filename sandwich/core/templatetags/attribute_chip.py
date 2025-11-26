from django import template
from django.utils.html import format_html

from sandwich.core.models.custom_attribute import CustomAttribute
from sandwich.core.models.custom_attribute import CustomAttributeEnum
from sandwich.core.service.custom_attribute_query import _parse_custom_attribute_id

register = template.Library()


@register.simple_tag()
def attribute_chip(attribute_name, label):
    attr_id = _parse_custom_attribute_id(attribute_name.replace("attr_", "").replace("_", "-"))
    if not attr_id:
        return None

    attribute = CustomAttribute.objects.get(id=attr_id)
    attr_enum = CustomAttributeEnum.objects.filter(attribute=attribute, label=label).first()
    color_tag = ""
    if attr_enum:
        color_tag = attr_enum.color_code

    return format_html('<div style="background-color: #{}">{}</div>', color_tag, label)
