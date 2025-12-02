from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from sandwich.core.models import Organization


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("slug", "name", "verified_list", "created_at", "updated_at")
    readonly_fields = ["verified_with_cta"]
    list_select_related = ["organizationverification"]
    prepopulated_fields = {"slug": ["name"]}
    search_fields = ("name", "slug")
    list_filter = ("created_at", "updated_at", "organizationverification")

    @admin.display(description="verified")
    def verified_list(self, obj):
        if hasattr(obj, "organizationverification"):
            url = reverse(
                "admin:core_organizationverification_change",
                args=[obj.organizationverification.id],
            )
            return format_html('<a href="{}">{}</a>', url, "True")
        return False

    @admin.display(description="verified")
    def verified_with_cta(self, obj):
        if text := self.verified_list(obj):
            return text

        url = reverse(
            "admin:core_organizationverification_add",
            query={"organization": obj.id},
        )
        html_string = '<span>False</span><br><br> <a href="{}">Verify Org -></a>'
        return format_html(html_string, url)
