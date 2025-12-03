from django import template
from django.template.loader import render_to_string

from sandwich.core.models.custom_attribute import CustomAttribute
from sandwich.core.models.custom_attribute import CustomAttributeEnum
from sandwich.core.service.custom_attribute_query import _parse_custom_attribute_id

register = template.Library()


@register.simple_tag()
def attribute_chip(attribute_name, label):
    attr_id = _parse_custom_attribute_id(attribute_name.replace("attr_", "").replace("_", "-"))
    if attr_id:
        attribute = CustomAttribute.objects.get(id=attr_id)
        attr_enum = CustomAttributeEnum.objects.filter(attribute=attribute, label=label).first()
        if attr_enum:
            color_tag = attr_enum.color_code

            if color_tag:
                return render_to_string(
                    "component/attribute_chip.html",
                    {
                        "label": label,
                        "color_tag": f"background-color: #{color_tag}",
                    },
                )

    return render_to_string(
        "component/attribute_chip.html",
        {
            "label": label,
        },
    )
