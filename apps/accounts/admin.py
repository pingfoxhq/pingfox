from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, UserProfile, UserActivation, Team, TeamMember


class UserProfileInline(admin.StackedInline):
    """Inline for UserProfile in UserAdmin."""

    model = UserProfile
    can_delete = False
    extra = 0


class UserActivationInline(admin.StackedInline):
    """Inline for UserActivation in UserAdmin."""

    model = UserActivation
    can_delete = False
    extra = 0
    readonly_fields = ("activation_code", "created_at", "expiration_date")


class UserAdmin(BaseUserAdmin):
    """Custom UserAdmin to include UserProfile and UserActivation inlines."""

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
            "",
        ),
    )


class TeamMemberInline(admin.TabularInline):
    """Inline for TeamMember in TeamAdmin."""

    model = TeamMember
    extra = 1
    autocomplete_fields = ["user"]


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    """Admin interface for Team model."""
    list_display = ("name", "created_at", "owner")
    search_fields = ("name",)
    inlines = [TeamMemberInline]
    autocomplete_fields = ["owner", "plan"]
    prepopulated_fields = {"slug": ("name",)}

    def get_queryset(self, request):
        """Override get_queryset to use select_related for owner."""
        queryset = super().get_queryset(request)
        return queryset.select_related("owner")

# Unregister the default User admin and register the custom UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

admin.site.site_header = "PingFox Admin"
admin.site.site_title = "PingFox Admin"

admin.site.index_title = "PingFox Administration"
