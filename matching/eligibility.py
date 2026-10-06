from django.utils import timezone


def evaluate_eligibility(student_profile, opportunity):
    """
    Evaluates hard eligibility criteria for an opportunity.
    Eligibility acts as a gate:
    If any mandatory criterion fails, is_eligible is False.
    Returns:
        dict: {
            'is_eligible': bool,
            'eligibility_score': float, # 30.0 if eligible, 0.0 if not
            'checks_passed': list of str,
            'failure_reasons': list of str
        }
    """
    checks_passed = []
    failure_reasons = []

    # 1. Active status check
    if not opportunity.is_active:
        failure_reasons.append("Opportunity is currently marked inactive.")

    # 2. Deadline check
    today = timezone.now().date()
    if opportunity.deadline < today:
        failure_reasons.append(f"Application deadline ({opportunity.deadline.strftime('%d %b %Y')}) has passed.")
    else:
        days_left = (opportunity.deadline - today).days
        checks_passed.append(f"Deadline valid ({days_left} days left - {opportunity.deadline.strftime('%d %b %Y')})")

    # 3. Branch eligibility check
    eligible_branches = list(opportunity.eligible_branches.all())
    if eligible_branches:
        if student_profile.branch and student_profile.branch in eligible_branches:
            checks_passed.append(f"Branch eligible ({student_profile.branch.code})")
        else:
            branch_codes = ", ".join([b.code for b in eligible_branches])
            student_branch = student_profile.branch.code if student_profile.branch else "Unspecified"
            failure_reasons.append(f"Branch {student_branch} not in required branches ({branch_codes})")
    else:
        checks_passed.append("Open to all engineering / academic branches")

    # 4. Academic Year eligibility check
    eligible_years = list(opportunity.eligible_years.all())
    if eligible_years:
        if student_profile.year and student_profile.year in eligible_years:
            checks_passed.append(f"Academic year eligible ({student_profile.year.name})")
        else:
            year_names = ", ".join([y.name for y in eligible_years])
            student_year = student_profile.year.name if student_profile.year else "Unspecified"
            failure_reasons.append(f"Academic year {student_year} not in eligible years ({year_names})")
    else:
        checks_passed.append("Open to all academic years")

    # 5. Minimum CGPA check
    if opportunity.minimum_cgpa > 0:
        if float(student_profile.cgpa) >= float(opportunity.minimum_cgpa):
            checks_passed.append(
                f"CGPA requirement satisfied ({student_profile.cgpa} >= {opportunity.minimum_cgpa})"
            )
        else:
            failure_reasons.append(
                f"CGPA ({student_profile.cgpa}) is below minimum requirement ({opportunity.minimum_cgpa})"
            )
    else:
        checks_passed.append("No minimum CGPA requirement")

    is_eligible = len(failure_reasons) == 0
    # Eligibility weight is 30% of final score
    eligibility_score = 30.0 if is_eligible else 0.0

    return {
        'is_eligible': is_eligible,
        'eligibility_score': eligibility_score,
        'checks_passed': checks_passed,
        'failure_reasons': failure_reasons,
    }
