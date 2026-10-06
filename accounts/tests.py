from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from students.models import StudentProfile


class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='teststudent',
            email='test@student.edu',
            password='Password123!',
            first_name='Test',
            last_name='User'
        )
        StudentProfile.objects.create(user=self.user)

    def test_registration_view(self):
        response = self.client.get(reverse('accounts:register'))
        self.assertEqual(response.status_code, 200)

        post_data = {
            'username': 'newstudent',
            'first_name': 'New',
            'last_name': 'Student',
            'email': 'new@student.edu',
            'password': 'SecurePassword123!',
            'confirm_password': 'SecurePassword123!',
            'college': 'Stanford',
            'cgpa': '8.50',
        }
        res_post = self.client.post(reverse('accounts:register'), post_data)
        self.assertRedirects(res_post, reverse('dashboard:student_dashboard'))
        self.assertTrue(User.objects.filter(username='newstudent').exists())
        self.assertTrue(StudentProfile.objects.filter(user__username='newstudent').exists())

    def test_login_and_logout(self):
        # Login
        login_res = self.client.post(reverse('accounts:login'), {
            'username': 'teststudent',
            'password': 'Password123!'
        })
        self.assertRedirects(login_res, reverse('dashboard:student_dashboard'))

        # Logout
        logout_res = self.client.post(reverse('accounts:logout'))
        self.assertRedirects(logout_res, reverse('accounts:login'))
