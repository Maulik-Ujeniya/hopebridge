from django.urls import path
from . import views

urlpatterns = [
    path('', views.program_list, name='program_list'),
    path('add/', views.program_create, name='program_create'),
    path('<int:program_id>/', views.program_detail, name='program_detail'),
    path('<int:program_id>/edit/', views.program_edit, name='program_edit'),
    path('<int:program_id>/delete/', views.program_delete, name='program_delete'),
]