from django.urls import path
from . import api


urlpatterns = [
    path("collect/", api.collect_data, name="collect_data"),
]