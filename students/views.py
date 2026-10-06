from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import StudentProfile, StudentSkill, Skill, Interest, Notification
from .forms import StudentProfileForm, UserUpdateForm, AddStudentSkillForm, StudentInterestsForm
from matching.skill_gap import (
    get_recommended_next_skills,
    get_platform_skill_demand,
    calculate_opportunity_skill_gap,
)
from matching.services import run_matching_engine_for_student
from matching.models import MatchResult


@login_required
def profile_view(request):
    try:
        profile = request.user.student_profile
    except StudentProfile.DoesNotExist:
        profile = StudentProfile.objects.create(user=request.user)

    student_skills = profile.student_skills.select_related('skill').all()
    user_interests = profile.interests.all()
    skill_form = AddStudentSkillForm()

    context = {
        'profile': profile,
        'student_skills': student_skills,
        'user_interests': user_interests,
        'skill_form': skill_form,
    }
    return render(request, 'students/profile.html', context)


@login_required
def profile_edit_view(request):
    try:
        profile = request.user.student_profile
    except StudentProfile.DoesNotExist:
        profile = StudentProfile.objects.create(user=request.user)

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = StudentProfileForm(request.POST, request.FILES, instance=profile)
        selected_interests = request.POST.getlist('interests')

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            profile.interests.set(selected_interests)
            # Re-run matching engine after profile update
            run_matching_engine_for_student(profile, save_to_db=True)
            messages.success(request, "Profile updated successfully! Recommendation scores have been refreshed.")
            return redirect('students:profile')
        else:
            messages.error(request, "Please check the form for errors.")
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = StudentProfileForm(instance=profile)

    all_interests = Interest.objects.all()
    user_interest_ids = set(profile.interests.values_list('id', flat=True))

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'all_interests': all_interests,
        'user_interest_ids': user_interest_ids,
        'profile': profile,
    }
    return render(request, 'students/profile_edit.html', context)


@login_required
def add_skill_view(request):
    if request.method == 'POST':
        profile = request.user.student_profile
        skill_id = request.POST.get('skill')
        skill_level = request.POST.get('skill_level', 'Intermediate')

        if skill_id:
            skill = get_object_or_404(Skill, id=skill_id)
            student_skill, created = StudentSkill.objects.update_or_create(
                student=profile,
                skill=skill,
                defaults={'skill_level': skill_level}
            )
            action = "added" if created else "updated"
            messages.success(request, f"Skill '{skill.name}' {action} at {skill_level} level!")
            # Recompute matches
            run_matching_engine_for_student(profile, save_to_db=True)
        else:
            messages.error(request, "Please select a valid skill.")

    return redirect('students:profile')


@login_required
def delete_skill_view(request, skill_id):
    if request.method == 'POST':
        profile = request.user.student_profile
        student_skill = get_object_or_404(StudentSkill, student=profile, skill_id=skill_id)
        skill_name = student_skill.skill.name
        student_skill.delete()
        messages.info(request, f"Skill '{skill_name}' removed from your profile.")
        # Recompute matches
        run_matching_engine_for_student(profile, save_to_db=True)

    return redirect('students:profile')


@login_required
def skill_gap_analysis_view(request):
    try:
        profile = request.user.student_profile
    except StudentProfile.DoesNotExist:
        profile = StudentProfile.objects.create(user=request.user)

    # 1. "What should I learn next?"
    recommended_skills = get_recommended_next_skills(profile, limit=8)

    # 2. Platform-wide skill demand analytics
    platform_demand = get_platform_skill_demand(limit=12)

    # 3. Opportunity-specific skill readiness breakdowns for top recommendations
    top_matches = MatchResult.objects.filter(student=profile, is_eligible=True).select_related('opportunity')[:6]
    detailed_gaps = []
    for match in top_matches:
        gap = calculate_opportunity_skill_gap(profile, match.opportunity)
        detailed_gaps.append({
            'match': match,
            'gap': gap,
        })

    context = {
        'profile': profile,
        'recommended_skills': recommended_skills,
        'platform_demand': platform_demand,
        'detailed_gaps': detailed_gaps,
        'student_skills_count': profile.student_skills.count(),
    }
    return render(request, 'students/skill_gap_analysis.html', context)


@login_required
def mark_notification_read_view(request, notification_id):
    notification = get_object_or_404(
        Notification, id=notification_id, student=request.user.student_profile
    )
    notification.is_read = True
    notification.save()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'ok'})
    return redirect('dashboard:index')


@login_required
def mark_all_notifications_read_view(request):
    request.user.student_profile.notifications.filter(is_read=False).update(is_read=True)
    messages.success(request, "All notifications marked as read.")
    return redirect('dashboard:index')
