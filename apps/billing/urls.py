from django.urls import path
from . import views

app_name = 'billing'
urlpatterns = [
    path('change/', views.change_plan, name='change_plan'),
    path('redeem/', views.redeem_code, name='redeem_code'),
]