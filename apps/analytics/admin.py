from django.contrib import admin
from .models import VisitorSession, PageView, Site
from .tasks import verify_site


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    """Admin interface for managing Sites."""

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
        ("Metadata", {"fields": ("created_at", "timezone", "verification_token", "form")}),
    )

    @admin.action(description="Verify selected sites")
    def verify_selected_sites(self, request, queryset):
        """Queue verification tasks for selected sites."""
        count = 0
        for site in queryset:
            verify_site.send(site.site_id)
            count += 1
        self.message_user(request, f"Verification task queued for {count} site(s).")


class PageViewInline(admin.TabularInline):
    """Inline admin interface for PageView model."""

    model = PageView
    extra = 0
    verbose_name = "Page View"
    verbose_name_plural = "Page Views"


@admin.register(VisitorSession)
class VisitorSessionAdmin(admin.ModelAdmin):
    """Admin interface for managing Visitor Sessions."""

    list_display = ("pf_id", "created_at", "last_seen", "user_agent")
    search_fields = ("pf_id", "user_agent")
    ordering = ("-created_at",)
    list_filter = ("created_at",)
    inlines = [PageViewInline]
