from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        (
            _("PingFox Info"),
            {
                "fields": (
                    "api_key",
                    "plan",
                    "avatar",
                    "plan_expires_at",
                    "referral_code",
                    "referred_by",
                    "accepted_terms",
                ),
            },
        ),
    )
    readonly_fields = ("api_key", "referral_code", "date_joined")
    list_display = ("username", "email", "plan", "plan_expires_at", "is_active")
    search_fields = ("username", "email", "referral_code")


admin.site.site_header = "PingFox Admin"
admin.site.site_title = "PingFox Admin"

admin.site.index_title = "PingFox Administration"
