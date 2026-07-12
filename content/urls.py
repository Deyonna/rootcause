from django.urls import path
from . import views

urlpatterns = [
    path('', views.writeup_list, name='writeup_list'),
    path('writeup/<int:pk>/', views.writeup_detail, name='writeup_detail'),
    path('writeup/<int:pk>/unlock/', views.writeup_unlock, name='writeup_unlock'),
]