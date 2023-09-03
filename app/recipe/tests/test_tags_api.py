"""Test Tags api"""

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag

from recipe.serializers import TagSerializer

# Notice that you use the router url here.
TAGS_URL = reverse('recipe:tag-list')

def detail_url(tag_id):
    return reverse('recipe:tag-detail', args=[tag_id])


def create_user(email = 'user@example.com', password = 'testpass123'):
    """Create and return a user"""
    return get_user_model().objects.create_user(email, password)

class PublicTagsApiTests(TestCase):
    """Test unauthenticated API requests"""

    def setUp(self):
        """This is the set up for the public test cases. Unauthenciated so no login"""
        self.client = APIClient()

    def test_auth_required(self):
        """Ensure that a user needs to be logged in in order to call any values."""

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateTagsApiTests(TestCase):
    """Tests the authenticated tags requests."""

    def setUp(self):
        """Force the authenticated login"""

        self.user = create_user()
        self.client= APIClient()
        self.client.force_authenticate(self.user)

    def test_retreive_tags(self):
        """test retrieving list of tags"""
        #Create directly in database
        Tag.objects.create(user=self.user, name='vegan')
        Tag.objects.create(user=self.user, name='pescitarian')

        # pull from url, will come back serialized
        res = self.client.get(TAGS_URL)

        # Standardize what order is going to return the data in.
        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.data, serializer.data)


    def test_users_can_only_see_their_own_tags(self):
        user2 = create_user(email='example2@example.com')

        tag = Tag.objects.create(user=self.user, name='omni')
        Tag.objects.create(user=user2, name='dog food')

        # prepare the test result
        res = self.client.get(TAGS_URL)

        # when parsing through this like a dict, it doesn't need to be
        # serialzied? We don't create a serializer because we are pulling
        # directly from the list.

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)
        self.assertEqual(res.data[0]['id'], tag.id)

    def test_tag_detail(self):
        """Test udating a tag"""
        tag = Tag.objects.create(user=self.user, name='after dinner')

        payload = {'name':'Dessert'}

        url = detail_url(tag.id)

        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])

    def test_tag_deletion(self):
        tag = Tag.objects.create(user = self.user, name = 'lunch')

        url = detail_url(tag.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        # you can call exists on a queryset to determine if anything was returned.
        tags = Tag.objects.filter(user=self.user)
        self.assertFalse(tags.exists())

