from django.urls import path
from . import views

app_name = "accounts"
urlpatterns = [
    path("", views.accounts_dashboard, name="index"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register_view, name="register"),
    path("activate/", views.activate_view, name="activate"),
    path("resend-activation/", views.resend_activation_view, name="resend_activation"),

    # Teams URLs
    path("over-limit/", views.teams_over_limit, name="teams_over_limit"),
    path("switch/", views.switch_team_view, name="teams_switch"),
    path("create/", views.team_create, name="teams_create"),
    path("edit/<slug:slug>/", views.team_edit, name="teams_edit"),
    path("list/", views.team_list, name="teams_list"),
    path("transfer/<slug:slug>/", views.team_transfer_ownership, name="teams_transfer_ownership"),
    path("<slug:slug>/", views.team_details, name="teams_details"),
]
