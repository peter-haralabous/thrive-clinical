from django import template
from django.http import QueryDict

register = template.Library()


# this code taken from https://code.djangoproject.com/ticket/10941#comment:33
@register.simple_tag
def query_string(*args, **kwargs):
    """
    Combines dictionaries of query parameters and individual query parameters
    and builds an encoded URL query string from the result.
    """
    query_dict = QueryDict(mutable=True)

    for a in args:
        query_dict.update(a)

    remove_keys = []

    for k, v in kwargs.items():
        if v is None:
            remove_keys.append(k)
        elif isinstance(v, list):
            query_dict.setlist(k, v)
        else:
            query_dict[k] = v

    for k in remove_keys:
        if k in query_dict:
            del query_dict[k]

    qs = query_dict.urlencode()
    if not qs:
        return ""
    return "?" + qs
