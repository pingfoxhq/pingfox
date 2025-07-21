from django.contrib import admin
from .models import Plan, PlanFeature, RedeemCode, generate_redeem_code, CodeRedemption
from django.utils.html import format_html
from apps.billing.seed import DEFAULT_FEATURES


class PlanFeatureInline(admin.TabularInline):
    model = PlanFeature
    extra = 0
    max_num = len(DEFAULT_FEATURES)
    fields = ("key", "value")
    can_delete = False
    readonly_fields = ("key",)
    verbose_name = "Feature"
    verbose_name_plural = "Plan Features"


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "price",
        "visible",
        "is_active",
        "highlighted",
        "ranking",
        "created_at",
        "feature_summary",
    )
    list_editable = ("visible", "is_active", "highlighted", "ranking")
    list_filter = ("is_active", "highlighted")
    search_fields = ("name", "slug", "description")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [PlanFeatureInline]
    ordering = ("ranking", "price")
    actions = ["add_default_features"]
    readonly_fields = ("created_at",)
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "slug",
                    "price",
                    "description",
                    "is_active",
                    "visible",
                    "highlighted",
                    "ranking",
                )
            },
        ),
        (
            "Advanced Options",
            {
                "classes": ("collapse",),
                "fields": ("created_at", "is_base_plan"),
                "description": "These options are for advanced users. Use with caution.",
            },
        ),
    )

    @admin.display(description="Features")
    def feature_summary(self, obj):
        """
        Returns a summary of the plan's features as a mini table.
        """
        features = obj.features.all()
        if not features:
            return "No features defined"

        feature_list = "<ul>"
        for feature in features:
            feature_list += f"<li><strong>{feature.key}:</strong> {feature.value}</li>"
        feature_list += "</ul>"

        return format_html(feature_list)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)

        obj = form.instance

        # Add default features only if none exist
        if not obj.features.exists():
            for key, value in DEFAULT_FEATURES.items():
                PlanFeature.objects.create(plan=obj, key=key, value=value)

    @admin.action(description="Add missing default features")
    def add_default_features(modeladmin, request, queryset):
        for plan in queryset:
            for key, value in DEFAULT_FEATURES.items():
                PlanFeature.objects.get_or_create(
                    plan=plan, key=key, defaults={"value": value}
                )


class CodeRedemptionInline(admin.TabularInline):
    model = CodeRedemption
    extra = 0
    readonly_fields = ("redeemed_at",)
    fields = ("redeem_code", "team", "redeemed_at")
    autocomplete_fields = ("team",)
    verbose_name = "Redeem Code"
    verbose_name_plural = "Redeem Codes"


@admin.register(RedeemCode)
class RedeemCodeAdmin(admin.ModelAdmin):
    list_display = ("code", "created_at")
    search_fields = ("code", "plan__name")
    fields = ("code", "description", "plan", "created_at", "is_active", "usage_limit", "used_count")
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)
    autocomplete_fields = ("plan",)
    inlines = [CodeRedemptionInline]

    def save_model(self, request, obj, form, change):
        if not obj.code:
            obj.code = generate_redeem_code()
        super().save_model(request, obj, form, change)
