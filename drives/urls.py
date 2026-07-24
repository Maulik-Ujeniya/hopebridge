from django.urls import path
from . import views

app_name = 'drives'

urlpatterns = [
    path('', views.drive_list, name='drive_list'),
    path('<int:drive_id>/', views.drive_detail, name='drive_detail'),
    path('<int:drive_id>/join/', views.join_drive, name='join_drive'),
]
