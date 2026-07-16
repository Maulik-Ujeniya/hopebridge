from django.urls import path
from . import views

urlpatterns = [
    path('', views.volunteer_list, name='volunteer_list'),
    path('add/', views.volunteer_create, name='volunteer_create'),
    path('<int:volunteer_id>/', views.volunteer_detail, name='volunteer_detail'),
]