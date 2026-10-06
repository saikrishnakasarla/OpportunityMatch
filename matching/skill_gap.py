from collections import Counter
from django.db.models import Count
from opportunities.models import Opportunity
from students.models import Skill, StudentProfile


def calculate_opportunity_skill_gap(student_profile, opportunity):
    """
    Computes the skill gap for a specific opportunity.
    Returns:
        dict: {
            'required_skills': list of str,
            'matched_skills': list of str,
            'missing_skills': list of str,
            'readiness_percentage': int,
            'readiness_message': str,
        }
    """
    required_skills = list(opportunity.required_skills.all())
    student_skill_ids = set(
        student_profile.student_skills.values_list('skill_id', flat=True)
    )

    matched = []
    missing = []

    for s in required_skills:
        if s.id in student_skill_ids:
            matched.append(s.name)
        else:
            missing.append(s.name)

    if required_skills:
        readiness_pct = int(round((len(matched) / len(required_skills)) * 100))
    else:
        readiness_pct = 100

    if missing:
        skills_str = ", ".join(missing)
        msg = (
            f"You are {readiness_pct}% aligned with this opportunity's skill requirements. "
            f"Adding [{skills_str}] to your profile would improve your compatibility score "
            f"under the platform's scoring model."
        )
    else:
        msg = (
            f"You are 100% aligned with this opportunity's technical requirements. "
            f"Your profile satisfies all required skills."
        )

    return {
        'required_skills': [s.name for s in required_skills],
        'matched_skills': matched,
        'missing_skills': missing,
        'readiness_percentage': readiness_pct,
        'readiness_message': msg,
    }


def get_platform_skill_demand(limit=10):
    """
    Aggregates skill demand across all active opportunities in the platform database.
    Returns a list of dicts: [{'name': 'Python', 'count': 25, 'category': '...'}, ...]
    """
    skills = (
        Skill.objects.filter(required_for_opportunities__is_active=True)
        .annotate(demand_count=Count('required_for_opportunities', distinct=True))
        .filter(demand_count__gt=0)
        .order_by('-demand_count', 'name')[:limit]
    )

    return [
        {
            'name': skill.name,
            'category': skill.category,
            'demand_count': skill.demand_count,
        }
        for skill in skills
    ]


def get_recommended_next_skills(student_profile, limit=6):
    """
    Identifies 'What should I learn next?' for a student.
    Analyzes all active opportunities relevant to the student's branch/year/domain
    and aggregates which missing skills occur most frequently.
    """
    student_skill_ids = set(
        student_profile.student_skills.values_list('skill_id', flat=True)
    )

    # Consider active opportunities that the student is eligible for or broadly match their branch/domain
    eligible_opps = Opportunity.objects.filter(is_active=True)
    if student_profile.branch:
        eligible_opps = eligible_opps.filter(
            eligible_branches__isnull=True
        ) | eligible_opps.filter(eligible_branches=student_profile.branch)

    # Collect missing skills count
    missing_skill_counter = Counter()

    for opp in eligible_opps.prefetch_related('required_skills').distinct():
        for skill in opp.required_skills.all():
            if skill.id not in student_skill_ids:
                missing_skill_counter[skill] += 1

    recommendations = []
    for skill, frequency in missing_skill_counter.most_common(limit):
        recommendations.append({
            'skill_id': skill.id,
            'name': skill.name,
            'category': skill.category,
            'frequency': frequency,
            'reason': f"Required by {frequency} opportunities matching your profile",
        })

    return recommendations
