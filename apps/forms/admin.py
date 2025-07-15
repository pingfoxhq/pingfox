from django.contrib import admin
from .models import Form, FormField, FormSubmission, FormStyle, models
from django.utils.html import format_html

@admin.register(FormSubmission)
class FormSubmissionAdmin(admin.ModelAdmin):
    list_display = ("form","submitted_at", "data")
    search_fields = ("form__name", "data")
    list_filter = ("submitted_at",)
    raw_id_fields = ("form",)
    list_per_page = 20
    


class FormFieldInline(admin.TabularInline):
    model = FormField
    extra = 1
    verbose_name = "Form Field"
    verbose_name_plural = "Form Fields"
    fields = (
        "field_type",
        "label",
        "required",
        "name",
        "placeholder",
        "validation_regex",
        "help_text",
        "choices",
    )
    prepopulated_fields = {"name": ("label",)}


class FormStyleInline(admin.TabularInline):
    model = FormStyle
    extra = 1
    verbose_name = "Form Style"
    verbose_name_plural = "Form Styles"
    fields = (
        "background_color",
        "text_color",
        "accent_color",
        "font_family",
        "logo",
        "custom_css_field",
    )
    readonly_fields = ("custom_css_field",)

    @admin.display(description="Custom CSS")
    def custom_css_field(self, obj):
        # show the custom CSS in a read-only field, and tell the user to edit it in the form style admin
        # Is creating a new FormStyle?
        if not obj.id:
            return format_html(
                '<span style="color: gray;">No custom CSS set. <br> Edit in <a href="/admin/forms/formstyle/add/">Form Style</a></span>'
            )
        if not obj.custom_css:
            return format_html(
                '<span style="color: gray;">No custom CSS set. <br> Edit in <a href="{}">Form Style</a></span>',
                f"/admin/forms/formstyle/{obj.id}/change/",
            )
        else:
            return format_html(
                '<pre style="white-space: pre-wrap; word-break: break-all;">{}</pre>',
                obj.custom_css,
            )


@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "created_at", "team")
    search_fields = ("name", "owner__username")
    list_filter = ("created_at",)
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("-created_at",)
    raw_id_fields = ("owner", "team")
    inlines = [FormStyleInline, FormFieldInline]
    autocomplete_fields = ["owner", "team"]

    list_per_page = 20
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # Use select_related to optimize queries for owner and team
        return queryset.select_related("owner", "team")


class FormFieldAdmin(admin.ModelAdmin):
    list_display = ("form", "field_type", "label", "required")
    search_fields = ("form__name", "label")
    list_filter = ("field_type", "required")
    raw_id_fields = ("form",)
    list_per_page = 20


@admin.register(FormStyle)
class FormStyleAdmin(admin.ModelAdmin):
    list_display = ("form", "background_color", "text_color", "accent_color")
    search_fields = ("form__name",)
    raw_id_fields = ("form",)
    list_per_page = 20
