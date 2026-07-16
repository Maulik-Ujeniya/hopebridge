from django.urls import path
from . import views

urlpatterns = [
    path('', views.donor_list, name='donor_list'),
]
