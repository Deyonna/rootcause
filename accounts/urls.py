from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views, admin_views
from .forms import StyledLoginForm

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', LoginView.as_view(template_name='accounts/login.html', authentication_form=StyledLoginForm), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('apply-author/', views.apply_author, name='apply_author'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),

    path('admin/', admin_views.admin_dashboard, name='admin_dashboard'),
    path('admin/users/', admin_views.admin_users, name='admin_users'),
    path('admin/users/<int:pk>/', admin_views.admin_user_detail, name='admin_user_detail'),
    path('admin/users/<int:pk>/toggle-role/', admin_views.admin_user_toggle_role, name='admin_user_toggle_role'),
    path('admin/users/<int:pk>/toggle-active/', admin_views.admin_user_toggle_active, name='admin_user_toggle_active'),
    path('admin/users/<int:pk>/delete/', admin_views.admin_user_delete, name='admin_user_delete'),

    path('admin/writeups/', admin_views.admin_writeups, name='admin_writeups'),
    path('admin/writeups/<int:pk>/edit/', admin_views.admin_writeup_edit, name='admin_writeup_edit'),
    path('admin/writeups/<int:pk>/delete/', admin_views.admin_writeup_delete, name='admin_writeup_delete'),

    path('admin/categories/', admin_views.admin_categories, name='admin_categories'),
    path('admin/categories/<int:pk>/edit/', admin_views.admin_category_edit, name='admin_category_edit'),
    path('admin/categories/<int:pk>/delete/', admin_views.admin_category_delete, name='admin_category_delete'),

    path('admin/plans/', admin_views.admin_plans, name='admin_plans'),
    path('admin/plans/<int:pk>/edit/', admin_views.admin_plan_edit, name='admin_plan_edit'),
    path('admin/plans/<int:pk>/delete/', admin_views.admin_plan_delete, name='admin_plan_delete'),

    path('admin/subscriptions/', admin_views.admin_subscriptions, name='admin_subscriptions'),

    path('admin/applications/', admin_views.admin_applications, name='admin_applications'),
    path('admin/applications/<int:pk>/', admin_views.admin_application_detail, name='admin_application_detail'),
    path('admin/applications/<int:pk>/<str:decision>/', admin_views.admin_review_application, name='admin_review_application'),

    path('admin/messages/', admin_views.admin_messages, name='admin_messages'),
    path('admin/messages/<int:pk>/delete/', admin_views.admin_message_delete, name='admin_message_delete'),
]
