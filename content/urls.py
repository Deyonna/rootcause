from django.urls import path
from . import views

urlpatterns = [
    path('', views.writeup_list, name='writeup_list'),
    path('writeup/<int:pk>/', views.writeup_detail, name='writeup_detail'),
    path('writeup/<int:pk>/unlock/', views.writeup_unlock, name='writeup_unlock'),
    path('writeup/<int:pk>/rate/', views.rate_writeup, name='rate_writeup'),
    path('writeup/<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('cart/add-subscription/<int:plan_id>/', views.add_subscription_to_cart, name='add_subscription_to_cart'),
    path('cart/remove/<int:index>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/checkout/', views.checkout, name='checkout'),
    path('subscriptions/', views.subscription_plans, name='subscription_plans'),
    path('my-writeups/', views.my_writeups, name='my_writeups'),
    path('writeup/new/', views.writeup_create, name='writeup_create'),
    path('writeup/<int:pk>/edit/', views.writeup_edit, name='writeup_edit'),
    path('writeup/<int:pk>/delete/', views.writeup_delete, name='writeup_delete'),
]