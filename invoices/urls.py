from django.urls import path
from . import views

app_name = 'invoices'

urlpatterns = [
    path('<int:donation_id>/', views.view_invoice, name='view_invoice'),
    path('<int:donation_id>/download/', views.download_invoice, name='download_invoice'),
]
