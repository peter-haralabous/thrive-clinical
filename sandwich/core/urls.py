import private_storage.urls
from django.conf import settings
from django.conf.urls.static import static
from django.templatetags.static import static as resolve_static
from django.urls import include
from django.urls import path
from django.views import defaults as default_views
from django.views.generic import RedirectView
from django.views.generic import TemplateView

from sandwich.core.views import healthcheck
from sandwich.core.views.account import account_delete
from sandwich.core.views.legal import legal_view

app_name = "core"
urlpatterns = [
    path("", TemplateView.as_view(template_name="pages/home.html"), name="home"),
    path("healthcheck/", healthcheck.healthcheck, name="healthcheck"),
    path("delete-account/", account_delete, name="account_delete"),
    path("legal/", legal_view, name="legal"),
    path("private-media/", include(private_storage.urls)),
    path("favicon.ico", RedirectView.as_view(url=resolve_static("images/favicons/favicon.ico"))),
]


if settings.SERVE_ERROR_VIEWS:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]

if settings.SERVE_MEDIA:
    urlpatterns.extend(static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT))
