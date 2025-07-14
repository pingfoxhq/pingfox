from django.contrib import admin
from .models import VisitorSession, PageView

class PageViewInline(admin.TabularInline):
    model = PageView
    extra = 0
    verbose_name = "Page View"
    verbose_name_plural = "Page Views"

@admin.register(VisitorSession)
class VisitorSessionAdmin(admin.ModelAdmin):
    list_display = ('pf_id', 'created_at', 'last_seen', 'user_agent')
    search_fields = ('pf_id', 'user_agent')
    ordering = ('-created_at',)
    list_filter = ('created_at',)
    inlines = [PageViewInline]