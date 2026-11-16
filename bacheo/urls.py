from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('atender/', views.atender_bache, name='atender_bache'),
    path('historial/', views.historial, name='historial'),
]