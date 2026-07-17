from django.urls import path
from . import views

urlpatterns = [
    path('', views.donation_list, name='donation_list'),
    path('add/', views.donation_create, name='donation_create'),
    path('<int:donation_id>/', views.donation_detail, name='donation_detail'),
    path('<int:donation_id>/edit/', views.donation_edit, name='donation_edit'),
    path('<int:donation_id>/delete/', views.donation_delete, name='donation_delete'),
    path('<int:donation_id>/invoice/', views.donation_invoice, name='donation_invoice'),
]