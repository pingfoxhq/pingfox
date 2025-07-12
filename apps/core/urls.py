from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("test-message/", views.test_message, name="test_message"),
]
