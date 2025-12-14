from django.urls import path

from apps.accounts import api

urlpatterns = [
    path("me/", api.MeView.as_view(), name="me"),
    path("logout/", api.LogoutView.as_view(), name="logout"),
    path("login/", api.CookieLoginView.as_view(), name="cookie_login"),
    path("refresh/", api.CookieRefreshView.as_view(), name="cookie_refresh"),
]