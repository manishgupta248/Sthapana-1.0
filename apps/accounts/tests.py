from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from .models import User


class UserModelTests(TestCase):
    def test_user_can_be_created(self):
        user = User.objects.create_user(username='testuser', password='testpass123')
        self.assertEqual(User.objects.count(), 1)
        self.assertTrue(user.check_password('testpass123'))

    def test_role_groups_exist(self):
        expected = {'Admin', 'EstablishmentOfficer', 'Clerk', 'ReadOnly'}
        actual = set(Group.objects.values_list('name', flat=True))
        self.assertTrue(expected.issubset(actual))


class LoginFlowTests(TestCase):
    def test_inactive_user_cannot_log_in(self):
        User.objects.create_user(username='pending', password='testpass123', is_active=False)
        logged_in = self.client.login(username='pending', password='testpass123')
        self.assertFalse(logged_in)

    def test_active_user_can_log_in(self):
        User.objects.create_user(username='activeuser', password='testpass123', is_active=True)
        logged_in = self.client.login(username='activeuser', password='testpass123')
        self.assertTrue(logged_in)

    def test_logged_out_visitor_redirected_to_login(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_registration_creates_inactive_user(self):
        response = self.client.post(reverse('register'), {
            'username': 'newperson',
            'email': 'newperson@example.com',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
        })
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username='newperson')
        self.assertFalse(user.is_active)