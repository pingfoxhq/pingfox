from django.urls import path
from . import views

app_name = "analytics"
urlpatterns = [
    path("", views.index, name="index"),
    path("create/", views.create_site, name="sites_create"),
    path("edit/<str:site_id>/", views.edit_site, name="sites_edit"),
    path("delete/<str:site_id>/", views.delete_site, name="sites_delete"),
    path("details/<str:site_id>/", views.site_details, name="sites_details"),
    path("verify/<str:site_id>/", views.send_verification, name="sites_verify"),
    path("chart/<str:site_id>/", views.site_chart, name="sites_chart"),
    path("download/<str:site_id>/", views.download_csv, name="sites_download_csv"),
]
