from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from students.models import StudentProfile
from matching.services import get_student_recommendations, run_matching_engine_for_student
from opportunities.models import SavedOpportunity


@login_required
def recommendations_list_view(request):
    """
    Dedicated Personalized Recommendations page.
    Implements the core USP: 'Don't Search for Opportunities. Let the System Search for You.'
    """
    try:
        profile = request.user.student_profile
    except StudentProfile.DoesNotExist:
        profile = StudentProfile.objects.create(user=request.user)

    category = request.GET.get('category', 'All')
    sort_by = request.GET.get('sort', 'score')
    only_eligible = request.GET.get('eligible', '1') == '1'

    recommendations_qs = get_student_recommendations(profile, category=category, sort_by=sort_by)

    if only_eligible:
        recommendations_qs = recommendations_qs.filter(is_eligible=True)

    saved_opportunity_ids = set(
        SavedOpportunity.objects.filter(student=profile).values_list('opportunity_id', flat=True)
    )

    # Summary counts
    total_matches = recommendations_qs.count()
    excellent_count = recommendations_qs.filter(overall_score__gte=90).count()
    strong_count = recommendations_qs.filter(overall_score__gte=75, overall_score__lt=90).count()
    moderate_count = recommendations_qs.filter(overall_score__gte=60, overall_score__lt=75).count()

    context = {
        'profile': profile,
        'recommendations': recommendations_qs,
        'saved_ids': saved_opportunity_ids,
        'selected_category': category,
        'selected_sort': sort_by,
        'only_eligible': only_eligible,
        'total_matches': total_matches,
        'excellent_count': excellent_count,
        'strong_count': strong_count,
        'moderate_count': moderate_count,
    }
    return render(request, 'recommendations/recommendations_list.html', context)


@login_required
def recalculate_matches_view(request):
    """
    Explicitly triggers the deterministic matching engine for the logged-in student.
    """
    try:
        profile = request.user.student_profile
        matches = run_matching_engine_for_student(profile, save_to_db=True)
        messages.success(
            request,
            f"Matching Engine executed! Analyzed {len(matches)} opportunities against your profile."
        )
    except Exception as e:
        messages.error(request, f"Error calculating matches: {str(e)}")

    return redirect('recommendations:list')
