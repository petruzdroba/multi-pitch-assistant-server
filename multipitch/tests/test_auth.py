# tests/test_auth_views.py
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
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

        # tokens renamed and nested user object
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)

        user_data = response.data['user']
        self.assertEqual(user_data['username'], self.valid_payload['username'])
        self.assertEqual(user_data['email'], self.valid_payload['email'])
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
        User.objects.create_user(username='testuser', email='existing@example.com', password='StrongPass123!')
        response = self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_signup_invalid_email(self):
        response = self.client.post(self.url, self.invalid_email_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)


class LoginViewTests(APITestCase):
    def setUp(self):
        self.url = reverse('login')
        self.user = User.objects.create_user(
            username='loginuser',
            email='login@example.com',
            password='StrongPass123!'
        )

        self.valid_payload = {
            'email': 'login@example.com',
            'password': 'StrongPass123!'
        }
        self.wrong_password_payload = {
            'email': 'login@example.com',
            'password': 'WrongPass123'
        }
        self.nonexistent_email_payload = {
            'email': 'nouser@example.com',
            'password': 'StrongPass123!'
        }
        self.missing_email_payload = {
            'password': 'StrongPass123!'
        }
        self.missing_password_payload = {
            'email': 'login@example.com'
        }

    def test_login_successful(self):
        response = self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # tokens renamed and nested user object
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)

        user_data = response.data['user']
        self.assertEqual(user_data['username'], self.user.username)
        self.assertEqual(user_data['email'], self.user.email)

    def test_login_wrong_password(self):
        response = self.client.post(self.url, self.wrong_password_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('non_field_errors' in response.data or 'detail' in response.data)

    def test_login_nonexistent_email(self):
        response = self.client.post(self.url, self.nonexistent_email_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('non_field_errors' in response.data or 'detail' in response.data)

    def test_login_missing_email(self):
        response = self.client.post(self.url, self.missing_email_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_login_missing_password(self):
        response = self.client.post(self.url, self.missing_password_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)


class MeViewTests(APITestCase):
    def setUp(self):
        self.url = reverse('me')
        self.user = User.objects.create_user(
            username='meuser',
            email='meuser@example.com',
            password='StrongPass123!'
        )
        self.refresh = RefreshToken.for_user(self.user)
        self.access_token = str(self.refresh.access_token)
    
    def test_me_authenticated(self):
        """Authenticated user receives user data and a refreshed access token"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.get(self.url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user', response.data)
        self.assertIn('access', response.data)
        self.assertEqual(response.data['user']['username'], self.user.username)
        self.assertEqual(response.data['user']['email'], self.user.email)
        self.assertNotEqual(response.data['access'], self.access_token)  # new token issued

    def test_me_unauthenticated(self):
        """Unauthenticated request returns user as None"""
        response = self.client.get(self.url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user', response.data)
        self.assertIsNone(response.data['user'])

    def test_me_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalidtoken123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)


    def test_me_missing_authorization_header(self):
        """No Authorization header behaves like unauthenticated"""
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data['user'])