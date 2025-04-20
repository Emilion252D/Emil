from django.urls import path
from django.contrib.auth.views import LogoutView
from django.contrib.auth import views as auth_views
from .views import (
    index, register_view, login_view, logout_view, profile_view,
    create_project, project_list, project_detail, edit_project,
    delete_project, accept_offer, project_chat, dashboard_view,
    leave_review
)

urlpatterns = [
    path('', index, name='home'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('profile/', profile_view, name='my_profile'),
    path('profile/<int:user_id>/', profile_view, name='profile'),
    path('projects/create/', create_project, name='create_project'),
    path('projects/', project_list, name='project_list'),
    path('projects/<int:pk>/', project_detail, name='project_detail'),
    path('projects/<int:pk>/edit/', edit_project, name='edit_project'),
    path('projects/<int:pk>/delete/', delete_project, name='delete_project'),
    path('offers/<int:pk>/accept/', accept_offer, name='accept_offer'),
    path('projects/<int:pk>/chat/', project_chat, name='project_chat'),
    path('logout/', LogoutView.as_view(template_name='logout.html'), name='logout'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('review/<int:user_id>/<int:project_id>/', leave_review, name='leave_review'),
]






