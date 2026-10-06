from django.shortcuts import render, redirect
from opportunities.models import Opportunity
from students.models import Skill, StudentProfile


def home_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff or request.user.is_superuser:
            return redirect('dashboard:admin_dashboard')
        return redirect('dashboard:student_dashboard')

    total_opportunities = Opportunity.objects.filter(is_active=True).count()
    total_skills = Skill.objects.count()
    total_students = StudentProfile.objects.count()
    featured_opportunities = Opportunity.objects.filter(is_active=True).order_by('?')[:3]

    context = {
        'total_opportunities': total_opportunities,
        'total_skills': total_skills,
        'total_students': total_students,
        'featured_opportunities': featured_opportunities,
    }
    return render(request, 'home.html', context)
