from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    path('skills/add/', views.add_skill_view, name='add_skill'),
    path('skills/<int:skill_id>/delete/', views.delete_skill_view, name='delete_skill'),
    path('skill-gaps/', views.skill_gap_analysis_view, name='skill_gaps'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read_view, name='mark_notification_read'),
    path('notifications/read-all/', views.mark_all_notifications_read_view, name='mark_all_notifications_read'),
]
