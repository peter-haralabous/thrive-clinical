from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render

from sandwich.core.models import Organization


@login_required
def home(request: HttpRequest) -> HttpResponse:
    organizations = Organization.objects.all()
    return render(request, "provider/home.html", {"organizations": organizations})


@login_required
def organization_home(request: HttpRequest, organization_id: int) -> HttpResponse:
    organization = get_object_or_404(Organization, id=organization_id)
    return render(request, "provider/organization_home.html", {"organization": organization})
