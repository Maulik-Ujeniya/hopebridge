from django.urls import path
from . import views

app_name = 'donations'

urlpatterns = [
    path('', views.donate_view, name='donate_view'),
    path('callback/', views.payment_callback, name='payment_callback'),
    path('success/<int:donation_id>/', views.donation_success, name='donation_success'),
    path('failed/', views.donation_failed, name='donation_failed'),
    path('dashboard/', views.donor_dashboard, name='donor_dashboard'),
    path('history/', views.my_donations, name='my_donations'),
    path('history/<int:donation_id>/', views.donation_detail, name='donation_detail'),
    path('resend-invoice/<int:donation_id>/', views.resend_invoice, name='resend_invoice'),
]