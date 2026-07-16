from django.urls import path
from . import views

urlpatterns = [
    path('', views.donor_list, name='donor_list'),
    path('add/', views.donor_create, name='donor_create'),
    path('<int:donor_id>/', views.donor_detail, name='donor_detail'),
]