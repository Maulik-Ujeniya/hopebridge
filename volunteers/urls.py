from django.urls import path
from . import views

urlpatterns = [
    path('', views.volunteer_list, name='volunteer_list'),
    path('<int:volunteer_id>/', views.volunteer_detail, name='volunteer_detail'),
]