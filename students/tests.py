from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from students.models import Branch, AcademicYear, Skill, Interest, StudentProfile, StudentSkill


class StudentProfileTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='johndoe',
            email='john@college.edu',
            password='password123',
            first_name='John',
            last_name='Doe'
        )
        self.branch = Branch.objects.create(name='Computer Science', code='CSE')
        self.year = AcademicYear.objects.create(year_number=3, name='3rd Year')
        self.profile = StudentProfile.objects.create(
            user=self.user,
            college='MIT',
            branch=self.branch,
            year=self.year,
            cgpa=8.20,
            preferred_mode='Online',
            preferred_type='Internship',
        )
        self.skill = Skill.objects.create(name='Python', category='Programming Languages')
        self.client.login(username='johndoe', password='password123')

    def test_profile_view(self):
        response = self.client.get(reverse('students:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'MIT')
        self.assertContains(response, 'Computer Science')

    def test_profile_edit(self):
        edit_data = {
            'first_name': 'Johnny',
            'last_name': 'Doe',
            'email': 'johnny@college.edu',
            'college': 'Harvard',
            'branch': self.branch.id,
            'year': self.year.id,
            'cgpa': '9.00',
            'preferred_mode': 'Hybrid',
            'preferred_type': 'Research',
            'preferred_duration': '3-6 Months',
            'preferred_location': 'Boston',
            'availability': 'Immediate',
        }
        response = self.client.post(reverse('students:profile_edit'), edit_data)
        self.assertRedirects(response, reverse('students:profile'))
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.college, 'Harvard')
        self.assertEqual(float(self.profile.cgpa), 9.00)
        self.assertEqual(self.profile.preferred_mode, 'Hybrid')

    def test_add_and_delete_skill(self):
        # Add Skill
        add_res = self.client.post(reverse('students:add_skill'), {
            'skill': self.skill.id,
            'skill_level': 'Advanced'
        })
        self.assertRedirects(add_res, reverse('students:profile'))
        self.assertTrue(StudentSkill.objects.filter(student=self.profile, skill=self.skill).exists())

        # Delete Skill
        del_res = self.client.post(reverse('students:delete_skill', kwargs={'skill_id': self.skill.id}))
        self.assertRedirects(del_res, reverse('students:profile'))
        self.assertFalse(StudentSkill.objects.filter(student=self.profile, skill=self.skill).exists())
