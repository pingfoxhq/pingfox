from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("onboarding/", views.onboarding, name="onboarding"),
    path("home/", views.home_unauth, name="home_unauth"),
]
