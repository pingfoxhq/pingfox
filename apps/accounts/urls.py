from django.urls import path
from . import views

app_name = "accounts"
urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register_view, name="register"),
    path("activate/", views.activate_view, name="activate"),
    path("profile/", views.edit_user_view, name="edit_user_view"),
]
