from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import home_view
from accounts import views as account_views
from students import views as student_views
from opportunities import views as opp_views
from recommendations import views as rec_views
from dashboard import views as dash_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Landing page
    path('', home_view, name='home'),

    # Direct routes as requested in Section 41
    path('register/', account_views.register_view, name='register'),
    path('login/', account_views.login_view, name='login'),
    path('logout/', account_views.logout_view, name='logout'),

    path('profile/', student_views.profile_view, name='profile'),
    path('profile/edit/', student_views.profile_edit_view, name='profile_edit'),
    path('skill-gaps/', student_views.skill_gap_analysis_view, name='skill_gaps'),

    path('dashboard/', dash_views.index_view, name='dashboard_root'),
    path('admin-dashboard/', dash_views.admin_dashboard_view, name='admin_dashboard_root'),

    path('recommendations/', rec_views.recommendations_list_view, name='recommendations_root'),
    path('saved/', opp_views.saved_opportunities_view, name='saved_root'),
    path('applications/', opp_views.applications_list_view, name='applications_root'),

    # App include namespaces
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('students/', include('students.urls', namespace='students')),
    path('opportunities/', include('opportunities.urls', namespace='opportunities')),
    path('recommendations/', include('recommendations.urls', namespace='recommendations')),
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
