from django.urls import path
from . import views

app_name = "teams"
urlpatterns = [
    path("switch/", views.switch_team_view, name="switch"),
    path("create/", views.team_create, name="create"),
    path("list/", views.team_list, name="list"),
    path("transfer/<slug:slug>/", views.team_transfer_ownership, name="transfer_ownership"),
    path("<slug:slug>/", views.team_detail, name="detail"),
]
