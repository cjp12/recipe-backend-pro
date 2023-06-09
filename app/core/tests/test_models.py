"""Tests for models"""

# We need to use test case because this will work with the db.
# Reference the db changes that are made in create_user.
from django.test import TestCase
# Get user model will stay up to date even if you updated it. BP
from django.contrib.auth import get_user_model


class ModelTests(TestCase):
    """Test Models"""

    def test_create_user_with_email_successful(self):
        """Users are able to be created with an email."""
        email = 'test@example.com'
        password = 'testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        # Ensures that the password was set.
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test that emails are normalized after processing."""

        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
            ['test5@example.com', 'test5@example.com']
        ]

        # Loop through emails and ensure they are normalized
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'sample123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test that users without an email raises an error"""

        # Use a context manager like with when testing for errors.
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', password='1234')

    def test_create_super_user(self):
        """Test the creation of the superuser"""
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'test123',
        )

        # is superuser is a benefit of the permissions mixin.
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)