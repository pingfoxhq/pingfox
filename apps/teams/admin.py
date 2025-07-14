from django.contrib import admin
from .models import Team, TeamMember


class TeamMemberInline(admin.TabularInline):
    model = TeamMember
    extra = 1
    autocomplete_fields = ["user"]


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at", "owner")
    search_fields = ("name",)
    inlines = [TeamMemberInline]
    autocomplete_fields = ["owner", "plan"]
    prepopulated_fields = {"slug": ("name",)}

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related("owner")
