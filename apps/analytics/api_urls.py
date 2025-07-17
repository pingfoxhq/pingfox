from django.urls import path
from . import api


urlpatterns = [
    path("collect/", api.collect_data, name="collect_data"),
    path("sites/<str:site_id>/chart-data/", api.site_chart_data_api, name="site_chart_data_api"),
]