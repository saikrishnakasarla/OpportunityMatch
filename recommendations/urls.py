from django.urls import path
from . import views

app_name = 'recommendations'

urlpatterns = [
    path('', views.recommendations_list_view, name='list'),
    path('recalculate/', views.recalculate_matches_view, name='recalculate'),
]
