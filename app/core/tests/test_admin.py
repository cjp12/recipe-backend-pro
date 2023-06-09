"""Test for the django admin modifications."""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client

class AdminSiteTests(TestCase):
    """Tests that will be run for the admin test.
    Set up will be run before."""
    # You are able to create class variables in the methods via self.
    # Don't need to be declared here.

    # Notice that the normal convention isn't used. Camel Casing.
    def setUp(self):
        """Create user and client"""

        # Create a super user
        self.client = Client()  # This will allow http requests
        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@example.com',
            password='testpass123'
        )

        # This will allow us to force the authentication to this user.
        self.client.force_login(self.admin_user)

        # Now we have a user that is created
        # Create a regular user
        self.user = get_user_model().objects.create_user(
            email='user@example.com',
            password = 'testpass123',
            name='Test User'
        )

    def test_users_list(self):
        """test that users are listed on the page."""
        url = reverse('admin:core_user_changelist')  # from doc
        res = self.client.get(url)  # Calls the url, with forced login.

        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_edit_user_page(self):
        """Test that users are able to be edited"""
        url = reverse('admin:core_user_change', args=[self.user.id])
        res = self.client.get(url)

        # Here we are able to determine if a page was loaded properly by
        # Looking at the status code that is returned.
        self.assertEqual(res.status_code,200)

    def test_create_user_page(self):
        """Test that the create user page works. UI allows adding users"""
        url = reverse('admin:core_user_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)