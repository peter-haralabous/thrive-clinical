from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.http import HttpResponse
from django.shortcuts import render

from sandwich.core.models import Organization


@login_required
def home(request: HttpRequest) -> HttpResponse:
    organizations = Organization.objects.all()
    return render(request, "provider/home.html", {"organizations": organizations})
