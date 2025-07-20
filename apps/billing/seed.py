# This dictionary contains the default features for new plans.
# It is used to ensure that every plan has a consistent set of features.
# By default, these features are for the "Free" plan.
DEFAULT_FEATURES = {
    "is_pro": "false",
    "sites_limit": "1",
    "pageviews": "10000",
    "forms_enabled": "true",
    "forms_limit": "3",
    "webhooks": "true",
    "wenhooks_limit": "3", # Same as forms_limit
    "script_badge": "false",
    "api_access": "true",
    "data_retention_days": "30",
    "import_enabled": "true",
    "export_enabled": "true",
    "backend_analytics": "false",
    "custom_domain": "false",
    "form_attachments": "false",
    "limit_reset_day": "1",
}


BASE_FREE_PLAN = {
    "name": "Base Free Plan",
    "slug": "base-free-plan",
    "price": 0,
    "description": "This is the base free plan for new teams.",
    "is_active": True,
    "visible": False,
    "highlighted": False,
    "ranking": 99,
    "is_base_plan": True,
}