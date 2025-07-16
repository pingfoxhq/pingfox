from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("", include("apps.core.urls")),
    path("dashboard/", include("apps.dashboard.urls")),
    path("accounts/", include("apps.accounts.urls")),
    path("analytics/", include("apps.analytics.urls")),
    path("sites/", include("apps.sites.urls")),
    path("forms/", include("apps.forms.urls")),
    path("f/", include("apps.forms.public_urls")),
    path("teams/", include("apps.teams.urls")),
    path("admin/", admin.site.urls),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
