from django.urls import path
from . import views

urlpatterns = [
    path('', views.writeup_list, name='writeup_list'),
    path('writeup/<int:pk>/', views.writeup_detail, name='writeup_detail'),
]