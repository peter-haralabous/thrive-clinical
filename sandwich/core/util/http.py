from django.http import HttpRequest

from sandwich.users.models import User


# https://github.com/typeddjango/django-stubs#how-can-i-create-a-httprequest-thats-guaranteed-to-have-an-authenticated-user
class AuthenticatedHttpRequest(HttpRequest):
    """If your view function is decorated with @login_required, use this type for the request parameter."""

    user: User
