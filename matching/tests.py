from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from students.models import Branch, AcademicYear, Skill, Interest, StudentProfile, StudentSkill
from opportunities.models import Opportunity
from matching.eligibility import evaluate_eligibility
from matching.scoring import compute_match_score
from matching.skill_gap import calculate_opportunity_skill_gap, get_recommended_next_skills


class MatchingEngineTests(TestCase):
    def setUp(self):
        # Academic structure
        self.branch_it = Branch.objects.create(name='Information Technology', code='IT')
        self.branch_mech = Branch.objects.create(name='Mechanical Engineering', code='ME')
        self.year_3 = AcademicYear.objects.create(year_number=3, name='3rd Year')
        self.year_1 = AcademicYear.objects.create(year_number=1, name='1st Year')

        # Skills
        self.skill_python = Skill.objects.create(name='Python', category='Programming Languages')
        self.skill_django = Skill.objects.create(name='Django', category='Web Development')
        self.skill_sql = Skill.objects.create(name='SQL', category='Databases')
        self.skill_docker = Skill.objects.create(name='Docker', category='Cloud & DevOps')
        self.skill_git = Skill.objects.create(name='Git', category='Tools')

        # Interests
        self.interest_ai = Interest.objects.create(name='Artificial Intelligence')
        self.interest_web = Interest.objects.create(name='Web Development')

        # Student User (Sai Krishna profile archetype)
        self.user = User.objects.create_user(username='saikrishna_test', password='password123')
        self.student = StudentProfile.objects.create(
            user=self.user,
            college='IIT',
            branch=self.branch_it,
            year=self.year_3,
            cgpa=8.00,
            preferred_mode='Online',
            preferred_type='Internship',
            preferred_duration='3-6 Months',
            availability='Immediate'
        )
        # Assign skills: Python, Django, SQL
        StudentSkill.objects.create(student=self.student, skill=self.skill_python, skill_level='Advanced')
        StudentSkill.objects.create(student=self.student, skill=self.skill_django, skill_level='Intermediate')
        StudentSkill.objects.create(student=self.student, skill=self.skill_sql, skill_level='Intermediate')
        self.student.interests.add(self.interest_ai, self.interest_web)

        # Opportunity: AI Internship requiring Python, Django, SQL, Git, Docker
        self.opp = Opportunity.objects.create(
            title='AI Engineering Internship',
            organization='Apex Labs',
            description='Applied AI engineering.',
            opportunity_type='Internship',
            domain='Artificial Intelligence',
            location='Remote',
            mode='Online',
            duration='3 Months',
            minimum_cgpa=7.00,
            deadline=timezone.now().date() + timezone.timedelta(days=30),
            application_url='https://example.com/apply',
            is_active=True
        )
        self.opp.eligible_branches.add(self.branch_it)
        self.opp.eligible_years.add(self.year_3)
        self.opp.required_skills.add(
            self.skill_python, self.skill_django, self.skill_sql, self.skill_git, self.skill_docker
        )
        self.opp.interests.add(self.interest_ai)

    def test_eligibility_evaluation_eligible(self):
        result = evaluate_eligibility(self.student, self.opp)
        self.assertTrue(result['is_eligible'])
        self.assertEqual(result['eligibility_score'], 30.0)
        self.assertEqual(len(result['failure_reasons']), 0)

    def test_eligibility_evaluation_ineligible_cgpa(self):
        # Create opportunity with higher CGPA requirement than student's 8.00
        high_cgpa_opp = Opportunity.objects.create(
            title='High Honor Fellowship',
            organization='Premier Inst',
            description='Elite fellowship.',
            opportunity_type='Fellowship',
            domain='Research',
            minimum_cgpa=9.50,
            deadline=timezone.now().date() + timezone.timedelta(days=20),
            application_url='https://example.com',
            is_active=True
        )
        result = evaluate_eligibility(self.student, high_cgpa_opp)
        self.assertFalse(result['is_eligible'])
        self.assertEqual(result['eligibility_score'], 0.0)
        self.assertTrue(any("CGPA" in reason for reason in result['failure_reasons']))

    def test_eligibility_evaluation_ineligible_branch(self):
        # Restrict opportunity to Mechanical only
        mech_opp = Opportunity.objects.create(
            title='Mechanical Design Internship',
            organization='Auto Dynamics',
            description='Automotive CAD.',
            opportunity_type='Internship',
            domain='Mechanical Engineering',
            minimum_cgpa=6.00,
            deadline=timezone.now().date() + timezone.timedelta(days=20),
            application_url='https://example.com',
            is_active=True
        )
        mech_opp.eligible_branches.add(self.branch_mech)

        result = evaluate_eligibility(self.student, mech_opp)
        self.assertFalse(result['is_eligible'])
        self.assertTrue(any("Branch" in reason for reason in result['failure_reasons']))

    def test_score_computation_and_explainability(self):
        score_data = compute_match_score(self.student, self.opp)

        self.assertTrue(score_data['is_eligible'])
        self.assertGreaterEqual(score_data['overall_score'], 70.0)

        # Matched skills should be Python, Django, SQL
        self.assertIn('Python', score_data['matched_skills'])
        self.assertIn('Django', score_data['matched_skills'])
        self.assertIn('SQL', score_data['matched_skills'])

        # Missing skills should be Git, Docker
        self.assertIn('Git', score_data['missing_skills'])
        self.assertIn('Docker', score_data['missing_skills'])

        # Explanation items should contain checkmarks
        self.assertTrue(any("Python" in item for item in score_data['explanation_items']))
        self.assertTrue(any("branch eligible" in item.lower() for item in score_data['explanation_items']))

    def test_skill_gap_analysis(self):
        gap = calculate_opportunity_skill_gap(self.student, self.opp)
        self.assertEqual(len(gap['matched_skills']), 3)
        self.assertEqual(len(gap['missing_skills']), 2)
        # 3 out of 5 required skills matched -> 60% readiness
        self.assertEqual(gap['readiness_percentage'], 60)
        self.assertIn("Git", gap['missing_skills'])
        self.assertIn("Docker", gap['missing_skills'])
        self.assertIn("Adding", gap['readiness_message'])

    def test_what_should_i_learn_next_recommendation(self):
        recs = get_recommended_next_skills(self.student, limit=5)
        # Git and Docker should be among the top recommended skills
        rec_names = [r['name'] for r in recs]
        self.assertTrue('Git' in rec_names or 'Docker' in rec_names)
