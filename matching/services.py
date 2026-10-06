from opportunities.models import Opportunity
from .models import MatchResult
from .scoring import compute_match_score


def run_matching_engine_for_student(student_profile, save_to_db=True):
    """
    Runs the deterministic matching engine for a given student against all active opportunities.
    Saves or updates MatchResult records in the database.
    Returns:
        list of MatchResult objects ordered by overall_score descending.
    """
    active_opportunities = Opportunity.objects.filter(is_active=True).prefetch_related(
        'eligible_branches', 'eligible_years', 'required_skills', 'interests'
    )

    results = []

    for opp in active_opportunities:
        score_data = compute_match_score(student_profile, opp)

        if save_to_db:
            match_obj, _ = MatchResult.objects.update_or_create(
                student=student_profile,
                opportunity=opp,
                defaults={
                    'overall_score': score_data['overall_score'],
                    'is_eligible': score_data['is_eligible'],
                    'eligibility_score': score_data['breakdown']['eligibility']['score'],
                    'skill_score': score_data['breakdown']['skills']['score'],
                    'interest_score': score_data['breakdown']['interests']['score'],
                    'preference_score': score_data['breakdown']['preferences']['score'],
                    'availability_score': score_data['breakdown']['availability']['score'],
                    'match_category': score_data['match_category'],
                    'matched_skills_data': score_data['matched_skills'],
                    'missing_skills_data': score_data['missing_skills'],
                    'explanation_items': score_data['explanation_items'],
                    'ineligibility_reasons': score_data['ineligibility_reasons'],
                }
            )
            results.append(match_obj)

    # Sort results by overall_score descending
    results.sort(key=lambda x: (x.is_eligible, x.overall_score), reverse=True)
    return results


def get_student_recommendations(student_profile, category=None, sort_by='score'):
    """
    Retrieves recommendations from MatchResult. If none exist yet, automatically runs the engine.
    """
    qs = MatchResult.objects.filter(student=student_profile).select_related('opportunity')

    if not qs.exists():
        run_matching_engine_for_student(student_profile, save_to_db=True)
        qs = MatchResult.objects.filter(student=student_profile).select_related('opportunity')

    if category and category != 'All':
        qs = qs.filter(match_category=category)

    if sort_by == 'deadline':
        qs = qs.order_by('opportunity__deadline', '-overall_score')
    elif sort_by == 'score_asc':
        qs = qs.order_by('overall_score')
    else:  # default 'score'
        qs = qs.order_by('-overall_score', 'opportunity__deadline')

    return qs
