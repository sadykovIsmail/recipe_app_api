"""Tests for the user API."""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL       = reverse('user:token')
ME_URL          = reverse('user:me')
JWT_LOGIN_URL   = reverse('user:jwt-login')
JWT_REFRESH_URL = reverse('user:jwt-refresh')
LOGOUT_URL      = reverse('user:logout')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


# ── Public endpoints ──────────────────────────────────────────────────────────

class PublicUserApiTests(TestCase):
    """Tests for unauthenticated user API endpoints."""

    def setUp(self):
        self.client = APIClient()

    # -- User creation --------------------------------------------------------

    def test_create_user_success(self):
        payload = {'email': 'test@example.com', 'password': 'testpass123', 'name': 'Test Name'}
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_with_email_exists_error(self):
        payload = {'email': 'test@example.com', 'password': 'testpass123', 'name': 'Test Name'}
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        payload = {'email': 'test@example.com', 'password': 'pw', 'name': 'Test name'}
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(get_user_model().objects.filter(email=payload['email']).exists())

    # -- Legacy DRF token -----------------------------------------------------

    def test_create_token_for_user(self):
        user_details = {'name': 'Test Name', 'email': 'test@example.com', 'password': 'test-user-password0123'}
        create_user(**user_details)
        res = self.client.post(TOKEN_URL, {'email': user_details['email'], 'password': user_details['password']})
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_bad_credentials(self):
        create_user(email='test@example.com', password='goodpass')
        res = self.client.post(TOKEN_URL, {'email': 'test@example.com', 'password': 'badpass'})
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self):
        res = self.client.post(TOKEN_URL, {'email': 'test@example.com', 'password': ''})
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # -- JWT ------------------------------------------------------------------

    def test_jwt_login_returns_access_and_refresh(self):
        """JWT login returns both access and refresh tokens."""
        create_user(email='jwt@example.com', password='testpass123', name='JWT User')
        res = self.client.post(JWT_LOGIN_URL, {'email': 'jwt@example.com', 'password': 'testpass123'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('access', res.data)
        self.assertIn('refresh', res.data)

    def test_jwt_login_bad_credentials(self):
        """JWT login with wrong password returns 401."""
        create_user(email='jwt@example.com', password='correct', name='JWT User')
        res = self.client.post(JWT_LOGIN_URL, {'email': 'jwt@example.com', 'password': 'wrong'})
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_jwt_refresh_returns_new_access_token(self):
        """Valid refresh token returns a new access token."""
        create_user(email='jwt@example.com', password='testpass123', name='JWT User')
        login_res = self.client.post(JWT_LOGIN_URL, {'email': 'jwt@example.com', 'password': 'testpass123'})
        refresh_token = login_res.data['refresh']

        res = self.client.post(JWT_REFRESH_URL, {'refresh': refresh_token})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('access', res.data)

    # -- Unauthenticated access -----------------------------------------------

    def test_retrieve_user_unauthorized(self):
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


# ── Private endpoints ─────────────────────────────────────────────────────────

class PrivateUserApiTests(TestCase):
    """Tests for authenticated user API endpoints."""

    def setUp(self):
        self.user = create_user(
            email='test@example.com',
            password='testpass123',
            name='Test Name',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {'name': self.user.name, 'email': self.user.email})

    def test_post_me_not_allowed(self):
        res = self.client.post(ME_URL, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        payload = {'name': 'Updated name', 'password': 'newpassword123'}
        res = self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_logout_blacklists_refresh_token(self):
        """Logout endpoint blacklists the refresh token."""
        # Get tokens for this user
        self.client.force_authenticate(user=None)   # use real JWT for this test
        login_res = self.client.post(
            JWT_LOGIN_URL,
            {'email': 'test@example.com', 'password': 'testpass123'},
        )
        self.assertEqual(login_res.status_code, status.HTTP_200_OK)
        access  = login_res.data['access']
        refresh = login_res.data['refresh']

        # Logout
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
        res = self.client.post(LOGOUT_URL, {'refresh': refresh})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Attempt to use the blacklisted refresh token
        res2 = self.client.post(JWT_REFRESH_URL, {'refresh': refresh})
        self.assertEqual(res2.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_missing_refresh_token_returns_400(self):
        """Logout with no refresh token returns 400."""
        res = self.client.post(LOGOUT_URL, {})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
