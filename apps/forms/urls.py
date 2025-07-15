from django.urls import path
from . import views

app_name = "forms"
urlpatterns = [
    path("", views.form_index, name="index"),
    path("list/", views.form_list, name="list"),
    path("create/", views.form_create, name="create"),
    path("edit/<slug:slug>", views.form_edit, name="edit"),
    path("convert/", views.convert_schema_to_form_view, name="convert"),
    path("builder/<slug:slug>/", views.form_builder, name="builder"),
    path("editor/<slug:slug>/", views.form_editor, name="editor"),
]
