from django.http import HttpRequest
from django.http import HttpResponse
from django.shortcuts import render


def home(request: HttpRequest) -> HttpResponse:
    return render(request, "provider/home.html")
