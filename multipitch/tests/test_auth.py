# tests/test_auth_views.py
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

class SignupViewTests(APITestCase):
    def setUp(self):
        self.url = reverse('signup')
        self.valid_payload = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'StrongPass123!'
        }
        self.weak_password_payload = {
            'username': 'weakuser',
            'email': 'weak@example.com',
            'password': '123'
        }
        self.missing_username_payload = {
            'email': 'nouser@example.com',
            'password': 'StrongPass123!'
        }
        self.invalid_email_payload = {
            'username': 'invalidemail',
            'email': 'notanemail',
            'password': 'StrongPass123!'
        }

    def test_signup_successful(self):
        response = self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['username'], self.valid_payload['username'])
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_signup_missing_username(self):
        response = self.client.post(self.url, self.missing_username_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_signup_weak_password(self):
        response = self.client.post(self.url, self.weak_password_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_signup_duplicate_username(self):
        # Create first user
        User.objects.create_user(username='testuser', password='StrongPass123!')
        response = self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_signup_invalid_email(self):
        response = self.client.post(self.url, self.invalid_email_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
