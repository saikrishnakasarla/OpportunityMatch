from django.urls import path
from . import views

app_name = 'opportunities'

urlpatterns = [
    path('', views.opportunity_list_view, name='list'),
    path('<int:pk>/', views.opportunity_detail_view, name='detail'),
    path('<int:pk>/save/', views.save_opportunity_toggle_view, name='save_toggle'),
    path('<int:pk>/apply/', views.apply_opportunity_view, name='apply'),
    path('saved/', views.saved_opportunities_view, name='saved'),
    path('applications/', views.applications_list_view, name='applications'),
    path('applications/<int:pk>/update/', views.update_application_status_view, name='update_application'),

    # Admin actions
    path('create/', views.opportunity_create_view, name='create'),
    path('<int:pk>/edit/', views.opportunity_edit_view, name='edit'),
    path('<int:pk>/delete/', views.opportunity_delete_view, name='delete'),
]
