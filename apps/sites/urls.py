from django.urls import path
from . import views


app_name = "sites"
urlpatterns = [
    path("", views.index, name="index"),
    path("list/", views.list_sites, name="list"),
    path("create/", views.create_site, name="create"),
    path("edit/<str:site_id>/", views.edit_site, name="edit"),
    path("delete/<str:site_id>/", views.delete_site, name="delete"),
    path("verify/<str:site_id>/", views.send_verification, name="verify"),
]
