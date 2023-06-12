"""Tests for the user api"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

# This is the name of the url that we are going to test.
CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')

def create_user(**params):
    """Create and return a new user. Whatever we provide to params."""
    return get_user_model().objects.create_user(**params)

# Public are unauthenticated requests
class PublicUserApiTests(TestCase):
    """Test the public features of the user API"""

    def setUp(self):
        self.client = APIClient()  # Allows for URL calls

    def test_create_user_success(self):
        """test creating a user is successful"""

        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test Name',
        }

        # Here we are catching the response for when we create an api
        # client, navigate to the url, pass it
        res = self.client.post(CREATE_USER_URL, payload)

        # Now for the assertions
        # Check to make sure that it is actually created.
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # Check to make sure the email exists
        user = get_user_model().objects.get(email=payload['email'])

        # Check to make sure that the password was set.
        # This is the best way to see if someone was actually created.
        self.assertTrue(user.check_password(payload['password']))

        # This makes sure that the password is not returned back to user.
        self.assertNotIn('password', res.data)


    def test_user_with_email_exists_error(self):
        """Check to see if duplicate email addresses are blocked"""

        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test Name',
        }

        # We create a user directly in terminal to ensure that they exist
        # Then we send a request via a client. Always test via client
        # This should be blocked in some way.
        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)

        # Make sure the request is bad.
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """Test that an error is fired if the password is less than 8 chars"""

        payload = {
            'email': 'test@example.com',
            'password': 'test',
            'name': 'Test Name',
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # The best way to check that a user is actually existing. get > 1?
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()  # Returns boolean.
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Creates a token for user with valid credentials."""

        user_details = {
            'name': 'Test Name',
            'email': 'test@example.com',
            'password': 'test12345'
        }

        create_user(**user_details)

        # This is the payload that is sent to the token api
        payload = {
            'email': user_details['email'],
            'password': user_details['password']
        }

        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_bad_user_credentials(self):
        """Returns an error if the user credentials are bad"""

        user_details = {
            'name': 'Test Name',
            'email': 'test@example.com',
            'password': 'test12345'
        }

        create_user(**user_details)

        payload = {
            'email': 'test@example.com',
            'password': 'badpass'
        }

        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_blank_password_(self):
        """Returns an error if the password is blank"""

        payload = {
            'email': 'test@example.com',
            'password': ''
        }

        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


    def retrieve_user_unauthorized(self):
        """Make sure that authentication is required for users."""

        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)



# Private requests are for requests that will require authentication.
# We handle this in different classes to handle auth in set up
class PrivateUserApiTests(TestCase):
    """Test that the user is required to log in to be able to use app"""

    def setUp(self):
        """Authenticate a test user to be able to use in each class"""
        # Create a client to be able to log in
        self.client = APIClient()

        # Directly create a user in the database, not via client
        self.user = create_user(**{
            'name': 'Test Name',
            'email':'test@example.com',
            'password': 'testpass12345' })

        # force a log in using that user. This will ensure that signing in
        # isn't an issue. All client requests now on.
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile(self):
        """Test retrieving the profile of the logged in user."""

        # Request the users profile
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Remember that you are checking a JSON response against an obj.
        self.assertEqual(res.data,{
            'email':self.user.email,
            'name': self.user.name
        })

    def test_posting_to_me_not_allowed(self):
        """Ensures that users are not able to post. PATCH ONLY"""
        # Remember that post is only used for creation.
        # need to send an empty dict as part of a post attempt, required.

        res = self.client.post(ME_URL, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test that there is a means to update the profile. PATCH."""
        payload = {'name': 'updated_name', 'password':'newpassword'}

        res = self.client.patch(ME_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Then refresh and check the data
        self.user.refresh_from_db()  # enabled via auth model

        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
