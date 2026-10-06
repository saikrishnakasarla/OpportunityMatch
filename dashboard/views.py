from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Avg, Count
from students.models import StudentProfile, Skill, Notification
from opportunities.models import Opportunity, Application, SavedOpportunity
from matching.models import MatchResult
from matching.services import get_student_recommendations, run_matching_engine_for_student
from matching.skill_gap import get_recommended_next_skills, get_platform_skill_demand


def is_admin(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


@login_required
def index_view(request):
    """
    Directs user to appropriate dashboard based on permissions.
    """
    if request.user.is_staff or request.user.is_superuser:
        return redirect('dashboard:admin_dashboard')
    return redirect('dashboard:student_dashboard')


@login_required
def student_dashboard_view(request):
    try:
        profile = request.user.student_profile
    except StudentProfile.DoesNotExist:
        profile = StudentProfile.objects.create(user=request.user)

    # Make sure matches are computed
    top_matches = get_student_recommendations(profile, sort_by='score').filter(is_eligible=True)[:4]
    if not top_matches.exists():
        run_matching_engine_for_student(profile, save_to_db=True)
        top_matches = get_student_recommendations(profile, sort_by='score').filter(is_eligible=True)[:4]

    # Metrics
    saved_ids = set(
        SavedOpportunity.objects.filter(student=profile).values_list('opportunity_id', flat=True)
    )
    total_saved = len(saved_ids)
    total_applied = Application.objects.filter(student=profile).count()

    # Upcoming deadlines for opportunities (next 30 days)
    today = timezone.now().date()
    upcoming_deadlines = Opportunity.objects.filter(
        is_active=True,
        deadline__gte=today,
        deadline__lte=today + timezone.timedelta(days=30)
    ).order_by('deadline')[:5]

    # Next recommended skill
    recommended_skills = get_recommended_next_skills(profile, limit=3)
    top_recommended_skill = recommended_skills[0] if recommended_skills else None

    # Notifications
    notifications = profile.notifications.all()[:5]

    context = {
        'profile': profile,
        'top_matches': top_matches,
        'saved_ids': saved_ids,
        'total_saved': total_saved,
        'total_applied': total_applied,
        'upcoming_deadlines': upcoming_deadlines,
        'top_recommended_skill': top_recommended_skill,
        'recommended_skills': recommended_skills,
        'notifications': notifications,
        'completion_pct': profile.completion_percentage,
    }
    return render(request, 'dashboard/student_dashboard.html', context)


@user_passes_test(is_admin)
def admin_dashboard_view(request):
    total_students = StudentProfile.objects.count()
    total_opportunities = Opportunity.objects.count()
    active_opportunities = Opportunity.objects.filter(is_active=True).count()
    total_applications = Application.objects.count()

    # Average match score
    avg_score_data = MatchResult.objects.filter(is_eligible=True).aggregate(avg=Avg('overall_score'))
    avg_match_score = round(avg_score_data['avg'] or 0.0, 1)

    # Opportunity type distribution
    type_counts = (
        Opportunity.objects.values('opportunity_type')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    type_labels = [item['opportunity_type'] for item in type_counts]
    type_values = [item['count'] for item in type_counts]

    # Platform skill demand
    skill_demand = get_platform_skill_demand(limit=8)
    skill_labels = [item['name'] for item in skill_demand]
    skill_values = [item['demand_count'] for item in skill_demand]

    # Recent items
    recent_students = StudentProfile.objects.select_related('user', 'branch', 'year').order_by('-created_at')[:8]
    recent_applications = Application.objects.select_related('student__user', 'opportunity').order_by('-applied_at')[:8]
    all_opportunities = Opportunity.objects.order_by('-created_at')[:10]

    context = {
        'total_students': total_students,
        'total_opportunities': total_opportunities,
        'active_opportunities': active_opportunities,
        'total_applications': total_applications,
        'avg_match_score': avg_match_score,
        'type_labels': type_labels,
        'type_values': type_values,
        'skill_labels': skill_labels,
        'skill_values': skill_values,
        'recent_students': recent_students,
        'recent_applications': recent_applications,
        'all_opportunities': all_opportunities,
    }
    return render(request, 'dashboard/admin_dashboard.html', context)
