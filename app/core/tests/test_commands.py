"""
Test custom Django management commands.
"""

# This is used to mock the behavior of the database.
from unittest.mock import patch

# This is one of the possibilies of the errors if we try to access to early.
from psycopg2 import OperationalError as Psycopg2Error

# This allows us to call the command that we are testing.
from django.core.management import call_command

# This could be an error depending on the stage that we
# request from the database.
from django.db.utils import OperationalError

# This allows us to test commands. We only need simple as it does not
# require any db set up.
from django.test import SimpleTestCase


# Here we are testing the patch method by navigating to the wait_for_db
# management command.
# Then we are going to call the command check.
# Here we are mocking the check method to see how it is going to return
# a response.
# Adding this decorator will add a new arg to each of the methods.
@patch('core.management.commands.wait_for_db.Command.check')
class CommandTests(SimpleTestCase):
    """Test commands"""

    def test_wait_for_db_ready(self, patched_check):
        """Test waiting for database if database ready."""

        # Mock the return value of the database.
        patched_check.return_value = True

        # Call the command, this should read the value set above.
        call_command('wait_for_db')

        # The command should execute only once, as when it executes,
        # it should read the returned_value = True and then continue.
        patched_check.assert_called_once_with(databases=['default'])

    # By including this here we are able to mock the sleeping of the database
    # without actually requiring it to sleep. Inside out.
    @patch('time.sleep')
    def test_wait_for_db_delay(self, patched_sleep, patched_check):
        """Test waiting for database when getting OperationalError"""

        # This odd looking data is a strange aspect of mocking.
        # The first 2 times that we call the method, raise psycopg2Error,
        # then 3 OperationalError then returns True.
        patched_check.side_effect = [Psycopg2Error] * 2 + \
            [OperationalError] * 3 + [True]

        call_command('wait_for_db')

        # There is a call counter for these basic commands.
        self.assertEqual(patched_check.call_count, 6)

        # This checks to ensure that it was called with the databases,
        # this checks the arguments that are being passed.
        patched_check.assert_called_with(databases=['default'])
