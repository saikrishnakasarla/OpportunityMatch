from .eligibility import evaluate_eligibility


def compute_match_score(student_profile, opportunity):
    """
    Computes a deterministic, explainable compatibility score between
    a student profile and an opportunity.

    Weights:
        Eligibility:    30%
        Skill Match:    30%
        Interest Match: 20%
        Preference:     10%
        Availability:   10%
        Total:         100%
    """
    # 1. Eligibility Gate (30%)
    eligibility_result = evaluate_eligibility(student_profile, opportunity)
    is_eligible = eligibility_result['is_eligible']
    eligibility_score = eligibility_result['eligibility_score']

    explanation_items = []
    for check in eligibility_result['checks_passed']:
        explanation_items.append(f"✓ {check}")

    # 2. Skill Matching (30%)
    required_skills = list(opportunity.required_skills.all())
    student_skill_map = {
        ss.skill_id: ss for ss in student_profile.student_skills.select_related('skill').all()
    }
    student_skill_ids = set(student_skill_map.keys())

    matched_skills = []
    missing_skills = []

    if required_skills:
        for skill in required_skills:
            if skill.id in student_skill_ids:
                matched_skills.append(skill)
                ss = student_skill_map[skill.id]
                explanation_items.append(f"✓ {skill.name} skill matched ({ss.skill_level})")
            else:
                missing_skills.append(skill)

        skill_ratio = len(matched_skills) / len(required_skills)
        raw_skill_score = skill_ratio * 30.0
    else:
        # If opportunity has no specific skills required, default full points
        skill_ratio = 1.0
        raw_skill_score = 30.0
        explanation_items.append("✓ No specific prerequisite skills mandated")

    skill_score = round(raw_skill_score, 1)

    # 3. Interest Matching (20%)
    student_interests = list(student_profile.interests.all())
    opp_interests = list(opportunity.interests.all())
    opp_domain = opportunity.domain.lower() if opportunity.domain else ""

    matched_interests = []
    if opp_interests:
        for interest in opp_interests:
            if interest in student_interests:
                matched_interests.append(interest)
                explanation_items.append(f"✓ {interest.name} interest matched")

        if len(opp_interests) > 0:
            interest_ratio = len(matched_interests) / len(opp_interests)
        else:
            interest_ratio = 0.5
    else:
        # Match domain keyword against student's interests
        matched_any = False
        for interest in student_interests:
            if interest.name.lower() in opp_domain or opp_domain in interest.name.lower():
                matched_interests.append(interest)
                matched_any = True
                explanation_items.append(f"✓ {interest.name} interest aligns with {opportunity.domain}")
                break

        interest_ratio = 1.0 if matched_any else (0.5 if student_interests else 0.3)

    # If student has at least one overlapping interest, give high marks
    if matched_interests and interest_ratio < 0.7:
        interest_ratio = 0.75  # Reward relevant interest overlap

    interest_score = round(min(20.0, interest_ratio * 20.0), 1)

    # 4. Preference Matching (10%)
    preference_points = 0.0

    # Type match (2.5 pts)
    if student_profile.preferred_type == 'Any' or student_profile.preferred_type == opportunity.opportunity_type:
        preference_points += 2.5
        explanation_items.append(f"✓ Opportunity type matched ({opportunity.opportunity_type})")
    else:
        preference_points += 0.5

    # Mode match (2.5 pts)
    if student_profile.preferred_mode == 'Any' or student_profile.preferred_mode == opportunity.mode:
        preference_points += 2.5
        explanation_items.append(f"✓ Work mode compatible ({opportunity.mode})")
    else:
        preference_points += 0.5

    # Duration match (2.5 pts)
    if student_profile.preferred_duration == 'Any':
        preference_points += 2.5
        explanation_items.append(f"✓ Duration compatible ({opportunity.duration})")
    elif student_profile.preferred_duration in opportunity.duration:
        preference_points += 2.5
        explanation_items.append(f"✓ Duration preference matched ({opportunity.duration})")
    else:
        preference_points += 1.5

    # Location match (2.5 pts)
    if not student_profile.preferred_location or opportunity.mode == 'Online':
        preference_points += 2.5
        if opportunity.mode == 'Online':
            explanation_items.append("✓ Location flexible (Remote / Online)")
    elif student_profile.preferred_location.lower() in opportunity.location.lower():
        preference_points += 2.5
        explanation_items.append(f"✓ Location matched ({opportunity.location})")
    else:
        preference_points += 1.0

    preference_score = round(preference_points, 1)

    # 5. Availability Matching (10%)
    avail_points = 10.0
    if student_profile.availability in ['Immediate', 'Flexible']:
        avail_points = 10.0
        explanation_items.append(f"✓ Availability aligned ({student_profile.availability})")
    elif student_profile.availability == 'Within 1 Month':
        avail_points = 9.0
        explanation_items.append(f"✓ Availability compatible ({student_profile.availability})")
    elif student_profile.availability == 'Summer Break':
        if 'summer' in opportunity.title.lower() or 'summer' in opportunity.description.lower():
            avail_points = 10.0
            explanation_items.append("✓ Summer break schedule perfectly aligned")
        else:
            avail_points = 7.0
            explanation_items.append("✓ Availability partly compatible (Summer Break)")
    else:
        avail_points = 8.0

    availability_score = round(avail_points, 1)

    # Calculate overall final score
    if is_eligible:
        overall_score = round(
            eligibility_score + skill_score + interest_score + preference_score + availability_score,
            1
        )
    else:
        # If ineligible under the gate rules, score is marked low / gated
        overall_score = round(
            (skill_score + interest_score + preference_score + availability_score) * 0.4,
            1
        )

    # Bound between 0 and 100
    overall_score = max(0.0, min(100.0, overall_score))

    # Match Category determination
    if overall_score >= 90:
        match_category = 'Excellent Match'
    elif overall_score >= 75:
        match_category = 'Strong Match'
    elif overall_score >= 60:
        match_category = 'Moderate Match'
    elif overall_score >= 40:
        match_category = 'Low Match'
    else:
        match_category = 'Poor Match'

    matched_skill_names = [s.name for s in matched_skills]
    missing_skill_names = [s.name for s in missing_skills]

    return {
        'overall_score': overall_score,
        'is_eligible': is_eligible,
        'match_category': match_category,
        'breakdown': {
            'eligibility': {'score': round(eligibility_score, 1), 'max': 30},
            'skills': {'score': round(skill_score, 1), 'max': 30},
            'interests': {'score': round(interest_score, 1), 'max': 20},
            'preferences': {'score': round(preference_score, 1), 'max': 10},
            'availability': {'score': round(availability_score, 1), 'max': 10},
            'total': {'score': round(overall_score, 1), 'max': 100},
        },
        'matched_skills': matched_skill_names,
        'missing_skills': missing_skill_names,
        'explanation_items': explanation_items,
        'ineligibility_reasons': eligibility_result['failure_reasons'],
    }
