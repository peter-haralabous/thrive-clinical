from django.contrib import admin

from sandwich.core.models import Consent
from sandwich.core.models import Document
from sandwich.core.models import Encounter
from sandwich.core.models import FormioSubmission
from sandwich.core.models import Invitation
from sandwich.core.models import Organization
from sandwich.core.models import Patient
from sandwich.core.models import Task
from sandwich.core.models import Template


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("slug", "name")
    prepopulated_fields = {"slug": ["name"]}
    search_fields = ("name", "slug")


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ("slug", "short_description", "organization")
    search_fields = ("slug",)
    list_filter = ("organization__slug",)

    @admin.display(description="Description", boolean=False)
    def short_description(self, obj):
        return obj.description.splitlines()[0] if obj.description else ""


admin.site.register(
    [Consent, Document, Encounter, FormioSubmission, Invitation, Patient, Task],
)
