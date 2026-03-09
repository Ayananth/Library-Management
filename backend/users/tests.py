from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase


class LogoutBlacklistTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="tester",
            email="tester@example.com",
            password="StrongPass#2026",
        )
        self.login_url = "/api/users/login/"
        self.logout_url = "/api/users/logout/"
        self.refresh_url = "/api/users/token/refresh/"

    def _get_tokens(self):
        response = self.client.post(
            self.login_url,
            {"username": "tester", "password": "StrongPass#2026"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response.data["access"], response.data["refresh"]

    def test_logout_blacklists_refresh_token(self):
        access, refresh = self._get_tokens()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        logout_response = self.client.post(
            self.logout_url,
            {"refresh": refresh},
            format="json",
        )
        self.assertEqual(logout_response.status_code, status.HTTP_205_RESET_CONTENT)

        refresh_response = self.client.post(
            self.refresh_url,
            {"refresh": refresh},
            format="json",
        )
        self.assertEqual(refresh_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_requires_authentication(self):
        _, refresh = self._get_tokens()
        response = self.client.post(
            self.logout_url,
            {"refresh": refresh},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_with_invalid_refresh_token(self):
        access, _ = self._get_tokens()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        response = self.client.post(
            self.logout_url,
            {"refresh": "invalid-token"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("refresh", response.data)
