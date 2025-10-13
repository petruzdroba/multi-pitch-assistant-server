from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class TokenRefreshViewTests(APITestCase):
    def setUp(self):
        self.url = reverse('token-refresh')  # assumes you named the route 'token-refresh'
        self.user = User.objects.create_user(
            username='tokenuser',
            email='token@example.com',
            password='StrongPass123!'
        )
        refresh = RefreshToken.for_user(self.user)
        self.valid_refresh = str(refresh)
        self.invalid_refresh = "totally.invalid.token"

    def test_refresh_success(self):
        """Should return a new access token when given a valid refresh token."""
        response = self.client.post(self.url, {"refresh": self.valid_refresh}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertTrue(isinstance(response.data["access"], str))
        self.assertGreater(len(response.data["access"]), 10)

    def test_missing_refresh_token(self):
        """Should return 400 when refresh token is missing."""
        response = self.client.post(self.url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertEqual(response.data["error"], "Refresh token required.")

    def test_invalid_refresh_token(self):
        """Should return 401 when refresh token is invalid."""
        response = self.client.post(self.url, {"refresh": self.invalid_refresh}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("error", response.data)
        self.assertEqual(response.data["error"], "Invalid or expired refresh token.")

    def test_empty_refresh_token(self):
        """Should return 400 when refresh token is an empty string."""
        response = self.client.post(self.url, {"refresh": ""}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertEqual(response.data["error"], "Refresh token required.")
