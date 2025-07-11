from django.contrib import admin
from .models import Plan


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "price", "is_active")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ["created_at"]
