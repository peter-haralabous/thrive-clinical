from django.contrib import admin

from sandwich.core.models import OrganizationVerification


@admin.register(OrganizationVerification)
class OrganizationVerificationAdmin(admin.ModelAdmin):
    list_display = ("organization", "approver", "created_at", "updated_at")
