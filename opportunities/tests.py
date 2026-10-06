from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from students.models import StudentProfile, Branch, Skill
from opportunities.models import Opportunity, SavedOpportunity, Application


class OpportunityCRUDAndPermissionTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.student_user = User.objects.create_user(
            username='student', password='password123', email='student@test.edu'
        )
        self.student_profile = StudentProfile.objects.create(user=self.student_user)

        self.admin_user = User.objects.create_user(
            username='admin_user', password='password123', email='admin@test.edu', is_staff=True
        )

        self.opportunity = Opportunity.objects.create(
            title='Junior Cloud Engineer',
            organization='Acme Corp',
            description='Exciting cloud engineering role.',
            opportunity_type='Internship',
            domain='Cloud Computing',
            location='Remote',
            mode='Online',
            duration='3 Months',
            minimum_cgpa=7.0,
            deadline=timezone.now().date() + timezone.timedelta(days=30),
            application_url='https://example.com/apply',
            is_active=True
        )

    def test_student_cannot_access_opportunity_create(self):
        self.client.login(username='student', password='password123')
        res = self.client.get(reverse('opportunities:create'))
        # Should redirect to login or deny permission
        self.assertEqual(res.status_code, 302)

    def test_admin_can_create_opportunity(self):
        self.client.login(username='admin_user', password='password123')
        post_data = {
            'title': 'AI Researcher',
            'organization': 'DeepMind Lab',
            'description': 'AI Research project.',
            'opportunity_type': 'Research',
            'domain': 'Artificial Intelligence',
            'location': 'London',
            'mode': 'Hybrid',
            'duration': '6 Months',
            'minimum_cgpa': '8.00',
            'deadline': (timezone.now().date() + timezone.timedelta(days=40)).isoformat(),
            'application_url': 'https://example.com/research',
            'is_active': True,
        }
        res = self.client.post(reverse('opportunities:create'), post_data)
        self.assertEqual(res.status_code, 302)
        self.assertTrue(Opportunity.objects.filter(title='AI Researcher').exists())

    def test_save_and_apply_opportunity(self):
        self.client.login(username='student', password='password123')

        # Save toggle
        save_res = self.client.get(reverse('opportunities:save_toggle', kwargs={'pk': self.opportunity.pk}))
        self.assertTrue(SavedOpportunity.objects.filter(student=self.student_profile, opportunity=self.opportunity).exists())

        # Unsave toggle
        save_res_2 = self.client.get(reverse('opportunities:save_toggle', kwargs={'pk': self.opportunity.pk}))
        self.assertFalse(SavedOpportunity.objects.filter(student=self.student_profile, opportunity=self.opportunity).exists())

        # Apply
        apply_res = self.client.post(
            reverse('opportunities:apply', kwargs={'pk': self.opportunity.pk}),
            {'notes': 'Applied with my latest resume'}
        )
        self.assertTrue(Application.objects.filter(student=self.student_profile, opportunity=self.opportunity).exists())
