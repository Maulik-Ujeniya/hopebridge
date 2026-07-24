from django.urls import path
from . import views

app_name = 'volunteers'

urlpatterns = [
    path('', views.volunteer_dashboard, name='volunteer_dashboard'),
    path('log/', views.log_work, name='log_work'),
    path('profile/', views.profile_update, name='profile_update'),
    path('history/', views.volunteer_history, name='volunteer_history'),
    path('calendar/', views.volunteer_calendar, name='volunteer_calendar'),
    path('certificates/', views.volunteer_certificates, name='volunteer_certificates'),
    path('apply/<int:drive_id>/', views.apply_for_drive, name='apply_for_drive'),
]