from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.utils import timezone
from .models import Opportunity, SavedOpportunity, Application
from .forms import OpportunityForm, ApplicationUpdateForm
from matching.scoring import compute_match_score
from matching.skill_gap import calculate_opportunity_skill_gap
from matching.models import MatchResult
from students.models import Notification, StudentProfile


def is_admin(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


def opportunity_list_view(request):
    """
    Explore all opportunities with search and filtering.
    For authenticated students, automatically attaches their match score.
    """
    query = request.GET.get('q', '').strip()
    opp_type = request.GET.get('type', '')
    mode = request.GET.get('mode', '')
    domain = request.GET.get('domain', '')
    min_score = request.GET.get('min_score', '')
    sort_by = request.GET.get('sort', 'deadline')

    opportunities = Opportunity.objects.filter(is_active=True).prefetch_related(
        'required_skills', 'interests', 'eligible_branches', 'eligible_years'
    )

    if query:
        opportunities = opportunities.filter(
            Q(title__icontains=query) |
            Q(organization__icontains=query) |
            Q(description__icontains=query) |
            Q(domain__icontains=query) |
            Q(required_skills__name__icontains=query)
        ).distinct()

    if opp_type:
        opportunities = opportunities.filter(opportunity_type=opp_type)

    if mode:
        opportunities = opportunities.filter(mode=mode)

    if domain:
        opportunities = opportunities.filter(domain__icontains=domain)

    # Attach match results for logged-in students
    student_profile = None
    matches_map = {}
    saved_ids = set()

    if request.user.is_authenticated:
        try:
            student_profile = request.user.student_profile
            saved_ids = set(
                SavedOpportunity.objects.filter(student=student_profile).values_list('opportunity_id', flat=True)
            )
            # Fetch precomputed match results
            matches = MatchResult.objects.filter(student=student_profile)
            for m in matches:
                matches_map[m.opportunity_id] = m
        except StudentProfile.DoesNotExist:
            pass

    opp_items = []
    for opp in opportunities:
        match_obj = matches_map.get(opp.id)
        # If no precomputed match, calculate on the fly if student logged in
        if not match_obj and student_profile:
            score_data = compute_match_score(student_profile, opp)
            score_val = score_data['overall_score']
            category = score_data['match_category']
            is_elig = score_data['is_eligible']
        elif match_obj:
            score_val = match_obj.overall_score
            category = match_obj.match_category
            is_elig = match_obj.is_eligible
        else:
            score_val = None
            category = None
            is_elig = None

        if min_score and score_val is not None:
            try:
                if score_val < float(min_score):
                    continue
            except ValueError:
                pass

        opp_items.append({
            'opportunity': opp,
            'match_score': score_val,
            'match_category': category,
            'is_eligible': is_elig,
            'is_saved': opp.id in saved_ids,
        })

    # Sort opportunities
    if sort_by == 'score_desc' and student_profile:
        opp_items.sort(key=lambda x: (x['match_score'] or 0), reverse=True)
    elif sort_by == 'newest':
        opp_items.sort(key=lambda x: x['opportunity'].created_at, reverse=True)
    else:  # deadline
        opp_items.sort(key=lambda x: x['opportunity'].deadline)

    # Distinct types and domains for filter dropdowns
    opportunity_types = Opportunity.TYPE_CHOICES
    domains = Opportunity.objects.filter(is_active=True).values_list('domain', flat=True).distinct()

    context = {
        'opportunities': opp_items,
        'total_count': len(opp_items),
        'query': query,
        'selected_type': opp_type,
        'selected_mode': mode,
        'selected_domain': domain,
        'selected_min_score': min_score,
        'selected_sort': sort_by,
        'opportunity_types': opportunity_types,
        'domains': sorted(set(filter(None, domains))),
    }
    return render(request, 'opportunities/opportunity_list.html', context)


def opportunity_detail_view(request, pk):
    """
    Displays complete opportunity details along with explainable match breakdown
    and skill gap for authenticated students.
    """
    opportunity = get_object_or_404(
        Opportunity.objects.prefetch_related(
            'required_skills', 'interests', 'eligible_branches', 'eligible_years'
        ),
        pk=pk
    )

    match_data = None
    skill_gap_data = None
    is_saved = False
    application = None

    if request.user.is_authenticated:
        try:
            student_profile = request.user.student_profile
            # Check save status
            is_saved = SavedOpportunity.objects.filter(
                student=student_profile, opportunity=opportunity
            ).exists()
            # Check application status
            application = Application.objects.filter(
                student=student_profile, opportunity=opportunity
            ).first()

            # Compute match and skill gap
            match_data = compute_match_score(student_profile, opportunity)
            skill_gap_data = calculate_opportunity_skill_gap(student_profile, opportunity)

            # Persist or update MatchResult
            MatchResult.objects.update_or_create(
                student=student_profile,
                opportunity=opportunity,
                defaults={
                    'overall_score': match_data['overall_score'],
                    'is_eligible': match_data['is_eligible'],
                    'eligibility_score': match_data['breakdown']['eligibility']['score'],
                    'skill_score': match_data['breakdown']['skills']['score'],
                    'interest_score': match_data['breakdown']['interests']['score'],
                    'preference_score': match_data['breakdown']['preferences']['score'],
                    'availability_score': match_data['breakdown']['availability']['score'],
                    'match_category': match_data['match_category'],
                    'matched_skills_data': match_data['matched_skills'],
                    'missing_skills_data': match_data['missing_skills'],
                    'explanation_items': match_data['explanation_items'],
                    'ineligibility_reasons': match_data['ineligibility_reasons'],
                }
            )
        except StudentProfile.DoesNotExist:
            pass

    context = {
        'opportunity': opportunity,
        'match_data': match_data,
        'skill_gap_data': skill_gap_data,
        'is_saved': is_saved,
        'application': application,
    }
    return render(request, 'opportunities/opportunity_detail.html', context)


@login_required
def save_opportunity_toggle_view(request, pk):
    """
    Saves or unsaves an opportunity for the student.
    """
    opportunity = get_object_or_404(Opportunity, pk=pk)
    try:
        student_profile = request.user.student_profile
    except StudentProfile.DoesNotExist:
        messages.error(request, "Student profile required.")
        return redirect('opportunities:detail', pk=pk)

    saved_obj = SavedOpportunity.objects.filter(student=student_profile, opportunity=opportunity).first()
    if saved_obj:
        saved_obj.delete()
        saved = False
        messages.info(request, f"Removed '{opportunity.title}' from your saved list.")
    else:
        SavedOpportunity.objects.create(student=student_profile, opportunity=opportunity)
        saved = True
        messages.success(request, f"Saved '{opportunity.title}' to your profile!")

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'saved': saved, 'count': student_profile.saved_opportunities.count()})

    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER')
    if next_url:
        return redirect(next_url)
    return redirect('opportunities:detail', pk=pk)


@login_required
def saved_opportunities_view(request):
    try:
        student_profile = request.user.student_profile
    except StudentProfile.DoesNotExist:
        return redirect('students:profile')

    saved_list = SavedOpportunity.objects.filter(
        student=student_profile
    ).select_related('opportunity').order_by('-saved_at')

    # Attach match results
    matches_map = {
        m.opportunity_id: m
        for m in MatchResult.objects.filter(student=student_profile)
    }

    items = []
    for s in saved_list:
        items.append({
            'saved': s,
            'opportunity': s.opportunity,
            'match': matches_map.get(s.opportunity_id),
        })

    context = {
        'items': items,
        'saved_count': len(items),
    }
    return render(request, 'opportunities/saved_opportunities.html', context)


@login_required
def apply_opportunity_view(request, pk):
    """
    Records an application in the student's tracker and provides the external application link.
    """
    opportunity = get_object_or_404(Opportunity, pk=pk)
    try:
        student_profile = request.user.student_profile
    except StudentProfile.DoesNotExist:
        messages.error(request, "Student profile required.")
        return redirect('opportunities:detail', pk=pk)

    notes = request.POST.get('notes', '')
    app_obj, created = Application.objects.get_or_create(
        student=student_profile,
        opportunity=opportunity,
        defaults={'status': 'Applied', 'notes': notes}
    )

    if not created and notes:
        app_obj.notes = notes
        app_obj.save()

    # Create internal notification
    Notification.objects.create(
        student=student_profile,
        title=f"Application Tracked: {opportunity.title}",
        message=f"You recorded an application for '{opportunity.title}' at {opportunity.organization}. You can update its status under Application Tracking.",
        notification_type='general'
    )

    messages.success(
        request,
        f"Application recorded for '{opportunity.title}'! You can track your progress here."
    )

    # If requested via POST with redirect_external
    if request.POST.get('redirect_external') == '1':
        return redirect(opportunity.application_url)

    return redirect('opportunities:applications')


@login_required
def applications_list_view(request):
    """
    Displays tracked applications for the student.
    """
    try:
        student_profile = request.user.student_profile
    except StudentProfile.DoesNotExist:
        return redirect('students:profile')

    applications = Application.objects.filter(
        student=student_profile
    ).select_related('opportunity').order_by('-applied_at')

    context = {
        'applications': applications,
        'status_choices': Application.STATUS_CHOICES,
    }
    return render(request, 'opportunities/applications.html', context)


@login_required
def update_application_status_view(request, pk):
    application = get_object_or_404(
        Application, pk=pk, student=request.user.student_profile
    )
    if request.method == 'POST':
        new_status = request.POST.get('status')
        notes = request.POST.get('notes', '')
        if new_status in dict(Application.STATUS_CHOICES):
            application.status = new_status
            application.notes = notes
            application.save()
            messages.success(request, f"Updated application status to '{new_status}'.")
    return redirect('opportunities:applications')


# Admin Views
@user_passes_test(is_admin)
def opportunity_create_view(request):
    if request.method == 'POST':
        form = OpportunityForm(request.POST)
        if form.is_valid():
            opportunity = form.save()
            messages.success(request, f"Opportunity '{opportunity.title}' created successfully!")
            return redirect('opportunities:detail', pk=opportunity.pk)
        else:
            messages.error(request, "Please correct the form errors.")
    else:
        form = OpportunityForm()

    return render(request, 'opportunities/opportunity_form.html', {'form': form, 'title': 'Add New Opportunity'})


@user_passes_test(is_admin)
def opportunity_edit_view(request, pk):
    opportunity = get_object_or_404(Opportunity, pk=pk)
    if request.method == 'POST':
        form = OpportunityForm(request.POST, instance=opportunity)
        if form.is_valid():
            opportunity = form.save()
            messages.success(request, f"Opportunity '{opportunity.title}' updated successfully!")
            return redirect('opportunities:detail', pk=opportunity.pk)
        else:
            messages.error(request, "Please correct the form errors.")
    else:
        form = OpportunityForm(instance=opportunity)

    return render(request, 'opportunities/opportunity_form.html', {'form': form, 'title': f'Edit {opportunity.title}', 'opportunity': opportunity})


@user_passes_test(is_admin)
def opportunity_delete_view(request, pk):
    opportunity = get_object_or_404(Opportunity, pk=pk)
    if request.method == 'POST':
        title = opportunity.title
        opportunity.delete()
        messages.success(request, f"Opportunity '{title}' deleted successfully.")
        return redirect('dashboard:admin_dashboard')

    return render(request, 'opportunities/opportunity_confirm_delete.html', {'opportunity': opportunity})
