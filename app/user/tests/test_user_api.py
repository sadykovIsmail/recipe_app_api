"""
Tests for the user API
"""

# Base class for Django tests.
# Django creates a temporary test database automatically.
from django.test import TestCase

# Returns the active User model (default or custom).
# Always use this instead of importing User directly.
from django.contrib.auth import get_user_model

# Converts a URL name into the actual URL path.
# Example: 'user:create' -> '/api/user/create/'
from django.urls import reverse

# REST framework client for making HTTP requests in tests.
from rest_framework.test import APIClient

# HTTP status codes (200, 201, 400, etc.)
from rest_framework import status


# URL for creating a user (resolved by name from urls.py)
CREATE_USER_URL = reverse('user:create')


def create_user(**params):
    """
    Helper function to create and return a new user.
    Used only inside tests to prepare test data.
    """
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """
    Tests for public (unauthenticated) user API endpoints.
    """

    def setUp(self):
        """
        Runs before each test.
        Creates a new API client instance.
        """
        self.client = APIClient()

    def test_create_user_success(self):
        """
        Test that creating a user with valid data succeeds.
        """
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test Name'
        }

        # Send POST request to create user endpoint
        res = self.client.post(CREATE_USER_URL, payload)

        # Check that the response status is 201 CREATED
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # Retrieve the user from the database
        user = get_user_model().objects.get(email=payload['email'])

        # Verify the password was hashed correctly
        self.assertTrue(user.check_password(payload['password']))

        # Ensure password is NOT returned in the API response
        self.assertNotIn('password', res.data)

    def test_user_with_email_exists_error(self):
        """
        Test that creating a user with an existing email fails.
        """
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test Name'
        }

        # Create a user with the same email first
        create_user(**payload)

        # Try to create another user with the same email
        res = self.client.post(CREATE_USER_URL, payload)

        # Expect a 400 BAD REQUEST error
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """
        Test that a password shorter than 5 characters is rejected.
        """
        payload = {
            'email': 'test@example.com',
            'password': 'pw',  # too short
            'name': 'Test name',
        }

        # Send POST request with invalid password
        res = self.client.post(CREATE_USER_URL, payload)

        # Expect validation error
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # Check that the user was NOT created in the database
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()

        self.assertFalse(user_exists)
