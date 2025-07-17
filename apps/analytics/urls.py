from django.urls import path
from . import views

app_name = "analytics"
urlpatterns = [
    path("", views.analytics_index, name="index"),
    path("chart/<str:site_id>/", views.site_chart, name="site_chart"),
    path("download/<str:site_id>/", views.download_csv, name="download_csv"),
]
