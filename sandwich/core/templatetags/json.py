import json

from django import template
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.html import format_html
from django.utils.safestring import mark_safe

register = template.Library()

_json_script_escapes = {
    ord(">"): "\\u003E",
    ord("<"): "\\u003C",
    ord("&"): "\\u0026",
}


@register.simple_tag(takes_context=True)
def json_script_safe(context, value, element_id=None):
    """
    CSP-safe version of json_script
    https://docs.djangoproject.com/en/5.2/ref/templates/builtins/#json-script
    """

    json_str = json.dumps(value, cls=DjangoJSONEncoder).translate(_json_script_escapes)
    if element_id:
        template = '<script id="{}" type="application/json" nonce="{}">{}</script>'
        args = (element_id, context.request.csp_nonce, mark_safe(json_str))  # noqa: S308 # this is for code
    else:
        template = '<script type="application/json" nonce="{}">{}</script>'
        args = (
            context.request.csp_nonce,
            mark_safe(json_str),  # noqa: S308 # this is for code
        )  # type: ignore[assignment]
    return format_html(template, *args)
