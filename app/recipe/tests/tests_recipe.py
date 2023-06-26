"""Test the recipe api"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe
from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer
)

RECIPE_URL = reverse('recipe:recipe-list')

def detail_url(recipe_id):
    """Create and return a recipe detail url"""
    # This is a function because we are going to be altering the address
    # Depending on which item we want to visit
    # Args will create args called in order?
    return reverse('recipe:recipe-detail', args=[recipe_id])

def create_recipe(user, **params):
    """Create and return a sample recipe"""

    # Create a default recipe to be created. Saves time
    defaults = {
        'title': 'sample recipe title',
        'time_minutes': 5,
        'price': Decimal('6.50'),
        'description': 'sample description'
    }

    # Update the defaults with any params.
    defaults.update(**params)

    # remember that due to the foreign key, the user must be present
    recipe = Recipe.objects.create(user = user, **defaults)

    # helper functions should return a recipe.
    return recipe

def create_user(**params):
    """Create and reutn a new user"""
    return get_user_model().objects.create_user(**params)


class PublicRecipeAPITests(TestCase):
    """Test Unauthenticated recipe requests. DISALLOWED"""

    def setUp(self):
        """Performs any setup that is required"""
        self.client = APIClient()

    def test_auth_required(self):
        """test that auth is required to call apis"""

        res = self.client.get(RECIPE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateRecipeAPITests(TestCase):
    """Test the authenticated recipe requests ALLOWED"""

    def setUp(self):
        """Login a user to the recipe api"""

        # Create a client
        self.client = APIClient()

        # Cleaner method of creating a user.
        self.user = create_user(email='user@example.com', password='test123')

        # force a sign in with that user
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test that recipes can be retrieved"""

        # Create a series of recipes
        create_recipe(self.user)
        create_recipe(self.user, title = 'orange chicken', price='5.5')

        # Get the content from the API - Test
        # because the recipes are being requested by the same user that
        # created them we would expect to see them all
        res = self.client.get(RECIPE_URL)

        # get the content from the database - Control
        recipes = Recipe.objects.all().order_by('-id')  # - = reverse order
        # to make sure that the data from the database is compariable to the
        # data that will be returned by the model view we need to run both
        # of them through the same serializer.
        serializer = RecipeSerializer(recipes, many=True)  # many = item list

        # Test. same input data, serializer ensures comp formatting
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_list_limited_to_user(self):
        """test that the items that are displayed are limited to the user"""

        other_user = create_user(
            email='test_other_user@example.com',
            password='otherpass123'
        )

        # Create recipes under another user
        create_recipe(other_user)
        create_recipe(self.user, time_minutes = 10)

        # log in as primary user to see if they are returned.
        res = self.client.get(RECIPE_URL)

        # control group should show only one. What do no recipes show?
        # Notice that we are filtering here. We only want to show same id.
        # We are setting the view to show the most recent things first.
        recipes = Recipe.objects.filter(user = self.user).order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_recipe_detail(self):
        """test get recipe detail"""

        # Create a recipe
        recipe = create_recipe(user = self.user)

        # use the id of the recipe above.
        url = detail_url(recipe.id)

        # Navigate to the url returned by the detail url function.
        res = self.client.get(url)

        # Serialize the data
        serializer = RecipeDetailSerializer(recipe)

        # check that the response data is the same as the serialized data
        # straight from the database.
        self.assertEqual(res.data, serializer.data)


    def test_create_recipe(self):
        """Here we would like to check whether we can pass a payload
        to the api to create a recipe. So we aren't going ot use the
        helper function."""

        payload = {
            'title': 'Sample recipe',
            'time_minutes': 30,
            'price': Decimal('5.99')
        }

        # you are just able to post to the main url to be able to post.
        res = self.client.post(RECIPE_URL, payload)
        # will always return an id response saying that it was created.

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id = res.data.get('id'))  # returned.

        # get returns a single model
        # filter returns a queryset, which is just a list of models.
        # the reason this wasn't working before is that I was attempting
        # to pull from the response, the issue was from the db.

        # loop through the response dict and ensure that it is the same
        # as the payload that was passed through to it. Each attr.
        # getattr (object, attr), should return the v from the res.
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)

        # Lastly check for the user, as this was defined at the client
        # level and not the payload level.
        self.assertEqual(recipe.user,self.user)


