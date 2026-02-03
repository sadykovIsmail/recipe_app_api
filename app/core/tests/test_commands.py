"""
Test custom Django management commands.

This file tests the `wait_for_db` command, which waits until
the database is available before Django continues starting.
"""

# patch is used to replace real functions/methods with mock objects
# so we can control their behavior in tests
from unittest.mock import patch

# psycopg2 OperationalError happens when PostgreSQL is not ready yet
# (e.g. container still starting)
from psycopg2 import OperationalError as Psycopg2Error

# call_command lets us run Django management commands in tests
from django.core.management import call_command

# Django's own OperationalError (raised after DB exists but not ready)
from django.db.utils import OperationalError

# SimpleTestCase does NOT require a database
# (important because DB is unavailable in these tests)
from django.test import SimpleTestCase


# Patch the `check` method of our wait_for_db command
# This replaces Command.check() with a mock object
@patch("core.management.commands.wait_for_db.Command.check")
# ⚠️ NOTE: "managemend" is a typo → should be "management"
class CommandTests(SimpleTestCase):
    """Test commands."""

    def test_wait_for_db_ready(self, patched_check):
        """
        Test waiting for database when database is ready immediately.
        """
        # Simulate the database being ready on first check
        patched_check.return_value = True

        # Run the management command: python manage.py wait_for_db
        call_command('wait_for_db')

        # Assert that the check method was called once
        # with the default database
        patched_check.assert_called_once_with(databases=['default'])

    # Patch time.sleep so tests don't actually wait
    @patch('time.sleep')
    def test_wait_for_db_delay(self, patched_sleep, patched_check):
        """
        Test waiting for database when OperationalError is raised.
        """

        # Simulate database startup behavior:
        # - First 2 calls → psycopg2 OperationalError (DB not started)
        # - Next 3 calls → Django OperationalError (DB exists but not ready)
        # - Last call → success (True)
        patched_check.side_effect = (
            [Psycopg2Error] * 2 +
            [OperationalError] * 3 +
            [True]
        )

        # Run the management command
        call_command('wait_for_db')

        # The command should retry until it succeeds
        # 2 psycopg2 errors + 3 django errors + 1 success = 6 calls
        self.assertEqual(patched_check.call_count, 6)

        # Verify the check was called with correct arguments
        patched_check.assert_called_with(databases=['default'])
