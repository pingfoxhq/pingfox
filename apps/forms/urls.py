from django.urls import path
from . import views

app_name = "forms"
urlpatterns = [
    path("", views.form_index, name="index"),
    path("list/", views.form_list, name="list"),
    path("create/", views.form_create, name="create"),
    path("edit/<slug:slug>", views.form_edit, name="edit"),
    path("save/<slug:slug>/", views.save_form, name="save"),
    path("freeze/<slug:slug>/", views.freeze_form, name="freeze"),
    path("save/<slug:slug>/htmx/", views.save_form_schema_view, name="save_htmx"),
    path("builder/<slug:slug>/", views.form_builder, name="builder"),
    path("editor/<slug:slug>/", views.form_editor, name="editor"),
    path("schema/<slug:slug>/", views.form_schema, name="schema"),
    path("convert/", views.convert_schema_to_form_view, name="convert"),
    path(
        "<slug:slug>/submissions/",
        views.submission_table_view,
        name="submission_list",
    ),
]
