from django.urls import path
from . import views

app_name = "script_urls"
urlpatterns = [
    path("pf.js", views.serve_pf_js, name="pf_js"),
]
