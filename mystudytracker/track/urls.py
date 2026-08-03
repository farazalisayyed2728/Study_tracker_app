from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('goal/new/', views.create_goal, name='create_goal'),
    path('home/<int:goal_id>/', views.goal_detail, name='home_detail'),
    path('track/<int:log_id>/update/', views.update_log, name='track_log'),
    path('api/log/<int:log_id>/toggle/', views.toggle_log_status, name='toggle_log_status'),
]