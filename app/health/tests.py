"""Tests for the health check endpoint."""
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient


HEALTH_URL = reverse('health-check')


class HealthCheckTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_health_check_returns_200(self):
        """A healthy system returns 200 with ok status."""
        res = self.client.get(HEALTH_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['status'], 'ok')
        self.assertEqual(res.data['database'], 'ok')

    def test_health_check_no_auth_required(self):
        """Health check is accessible without authentication."""
        res = self.client.get(HEALTH_URL)
        self.assertNotEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_health_check_db_down_returns_503(self):
        """When the database is unreachable the endpoint returns 503."""
        from django.db import OperationalError
        with patch('health.views.connection') as mock_conn:
            mock_conn.cursor.side_effect = OperationalError('db is down')
            res = self.client.get(HEALTH_URL)
        self.assertEqual(res.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertEqual(res.data['status'], 'degraded')
        self.assertEqual(res.data['database'], 'unavailable')
