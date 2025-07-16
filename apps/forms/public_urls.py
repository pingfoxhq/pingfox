from .views import form_public_view, form_submit_view
from django.urls import path


app_name = "public_forms"
urlpatterns = [
    path("<slug:slug>/", form_public_view, name="public"),
    path("<slug:slug>/submit", form_submit_view, name="submit"),
]
