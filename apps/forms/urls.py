from django.urls import path
from . import views

app_name = "forms"
urlpatterns = [
    path("", views.form_index, name="index"),
    path("list/", views.form_list, name="list"),
    path("create/", views.form_create, name="create"),
    path("builder/<slug:slug>/", views.form_builder, name="builder"),
]
