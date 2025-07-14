from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, UserProfile, UserActivation


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    extra = 0


class UserActivationInline(admin.StackedInline):
    model = UserActivation
    can_delete = False
    extra = 0
    readonly_fields = ("activation_code", "created_at", "expiration_date")


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline, UserActivationInline)
    list_display = ("username", "email", "first_name", "last_name", "is_staff")
    list_filter = ("is_staff", "is_active")
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email")}),
        (
            _("Permissions"),
            {"fields": ("is_staff", "is_active", "groups", "user_permissions")},
        ),
        (_("Important dates"), {"fields": ("last_login",)}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email", "password1", "password2"),
            },
            ""
        ),
        
    )


admin.site.unregister(User)
admin.site.register(User, UserAdmin)

admin.site.site_header = "PingFox Admin"
admin.site.site_title = "PingFox Admin"

admin.site.index_title = "PingFox Administration"
