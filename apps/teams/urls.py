from django.urls import path
from . import views

app_name = "teams"
urlpatterns = [
    path("create/", views.team_create, name="create"),
    path('switch/', views.switch_team, name='switch'),
]