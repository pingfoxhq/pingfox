from django.urls import path
from . import views


app_name = "core"
urlpatterns = [
    path("", views.home, name="home"),
    path("onboarding/", views.onboarding, name="onboarding"),
    path("home/", views.home_unauth, name="home_unauth"),
    path(
        ".well-known/pingfox-verification.txt",
        views.verification_token,
        name="verification_token",
    ),
]
