from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.notification_list, name='notification_list'),
    path('api/unread/', views.get_unread_notifications, name='get_unread'),
    path('mark-read/<int:notification_id>/', views.mark_read, name='mark_read'),
    path('mark-all-read/', views.mark_all_read, name='mark_all_read'),
    path('archive/<int:notification_id>/', views.archive_notification, name='archive'),
    path('delete/<int:notification_id>/', views.delete_notification, name='delete'),
]
