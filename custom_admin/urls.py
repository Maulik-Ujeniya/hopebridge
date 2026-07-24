from django.urls import path
from . import views

app_name = 'custom_admin'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    
    # Users
    path('users/', views.user_list, name='user_list'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
    path('users/<int:user_id>/toggle/', views.toggle_user_status, name='toggle_user_status'),
    path('users/<int:user_id>/assign_role/', views.assign_role, name='assign_role'),
    
    # Donations
    path('donations/', views.donation_list, name='donation_list'),
    path('donations/<int:donation_id>/allocate/', views.allocate_donation, name='allocate_donation'),
    path('donations/<int:donation_id>/refund/', views.refund_donation, name='refund_donation'),
    
    # Drives
    path('drives/', views.drive_list, name='drive_list'),
    path('drives/create/', views.drive_form, name='drive_create'),
    path('drives/<int:drive_id>/update/', views.drive_form, name='drive_update'),
    
    # Announcements
    path('notifications/send/', views.notification_send, name='notification_send'),
    
    # Reports & Settings
    path('reports/', views.reports_view, name='reports_view'),
    path('settings/', views.settings_view, name='settings_view'),
]
