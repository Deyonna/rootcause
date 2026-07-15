from django.urls import path
from . import views

urlpatterns = [
    path('', views.writeup_list, name='writeup_list'),
    path('writeup/<int:pk>/', views.writeup_detail, name='writeup_detail'),
    path('writeup/<int:pk>/unlock/', views.writeup_unlock, name='writeup_unlock'),
    path('writeup/<int:pk>/rate/', views.rate_writeup, name='rate_writeup'),
    path('writeup/<int:pk>/comment/', views.add_comment, name='add_comment'),
]