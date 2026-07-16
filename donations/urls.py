from django.urls import path
from . import views

urlpatterns = [
    path('', views.donation_list, name='donation_list'),
    path('<int:donation_id>/', views.donation_detail, name='donation_detail'),
]