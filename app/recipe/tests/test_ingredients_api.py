"""test for the ingredients api"""

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient

from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredient-list')

def detail_url(ingredient_id):
    """create and return an incredient detail url"""
    return reverse('recipe:ingredient-detail', args=[ingredient_id])

def create_user(email='user@example.com', password = 'testpass1234'):
    return get_user_model().objects.create_user(email, password)

class PublicIngredientsApiTests(TestCase):
    """test unauthenticated API requests"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that auth is required if ingredients are requested."""

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTests(TestCase):
    """Test unauthenticated api requests"""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        # Force the client to log in.
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients(self):
        """Test Retrieving a list of ingredients"""
        Ingredient.objects.create(user = self.user, name='sugar')
        Ingredient.objects.create(user = self.user, name='spice')

        res = self.client.get(INGREDIENTS_URL)

        # Database is entirely refreshed for each and every test.

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many = True)

        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """test that the ingredients are limited to the user"""
        user2 = create_user(email='example2@example.com', password='example2pass123')

        Ingredient.objects.create(user= user2, name='vinegar')
        positive_ingredient = Ingredient.objects.create(user= self.user, name='honey')

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data),1)
        self.assertEqual(res.data[0]['name'], positive_ingredient.name)
        self.assertEqual(res.data[0]['id'], positive_ingredient.id)

    def test_update_ingredient(self):
        """Test updating an ingredient."""
        ingredient = Ingredient.objects.create(user=self.user, name="cilantro")

        payload = {'name':'Coriander'}
        url = detail_url(ingredient.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()
        self.assertEqual(ingredient.name, payload['name'])

    def test_delete_ingredient(self):
        """Test the deletion of the ingredient"""
        ingredient = Ingredient.objects.create(user = self.user, name='Lettuce')

        url = detail_url(ingredient.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        ingredients = Ingredient.objects.filter(user = self.user)
        self.assertNotIn(ingredient, ingredients)
        self.assertFalse(ingredients.exists())

