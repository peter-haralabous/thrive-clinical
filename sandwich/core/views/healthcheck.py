from django.http import JsonResponse
from django.utils import timezone


def healthcheck(request):
    """
    Healthcheck endpoint.
    """
    return JsonResponse({"datetime": timezone.now()})
