from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView,
)

urlpatterns = [
    path("", include("apps.core.urls")),
    path("", include("apps.analytics.script_urls")),
    path("accounts/", include("apps.accounts.urls")),
    path("analytics/", include("apps.analytics.urls")),
    path("billing/", include("apps.billing.urls")),
    path("forms/", include("apps.forms.urls")),
    path("f/", include("apps.forms.public_urls")),
    path("admin/", admin.site.urls),
    path(
        "api/",
        include(
            [
                path(
                    "auth/",
                    include(
                        [
                            path(
                                "",
                                include("apps.accounts.api_urls"),
                            ),
                        ]
                    ),
                ),
                path("analytics/", include("apps.analytics.api_urls")),
            ],
        ),
    ),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
