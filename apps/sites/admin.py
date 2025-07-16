from django.contrib import admin
from .models import Site
from .tasks import verify_site


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "domain",
        "site_id",
        "is_verified",
        "is_active",
        "created_at",
    )
    search_fields = ("name", "domain", "site_id")
    list_filter = ("is_verified", "is_active")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "site_id", "verification_token")
    actions = ["verify_selected_sites"]

    fieldsets = (
        (None, {"fields": ("team", "owner", "name", "domain", "site_id")}),
        ("Status", {"fields": ("is_verified", "is_active")}),
        ("Advanced Options", {"fields": ("pageview_limit_override",)}),
        ("Metadata", {"fields": ("created_at", "timezone", "verification_token")}),
    )

    @admin.action(description="Verify selected sites")
    def verify_selected_sites(self, request, queryset):
        count = 0
        for site in queryset:
            verify_site.send(site.site_id)
            count += 1
        self.message_user(request, f"Verification task queued for {count} site(s).")
