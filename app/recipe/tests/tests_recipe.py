"""Test the recipe api"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Recipe,
    Tag,
    Ingredient
)
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


    def test_partial_update(self):
        """Test partial update"""

        original_link = 'https://example.com/recipe.pdf'

        recipe = create_recipe(
            user = self.user,
            title = 'Sample Recipe',
            link = original_link
        )

        payload = {'title': 'New Recipe Title'}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # We have created the recipe and stored it in a variable.
        # Then we made changes via the endpoint. Now we need to refresh our
        # variable for accurate testing. So that means its a copy
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)

    def test_full_update(self):
        """Test full update of recipe"""

        recipe = create_recipe(
            user = self.user,
            title = 'Sample Recipe title',
            link = 'https://example.com/OldRecipe.pdf',
            description = 'Sample Description'
        )

        # Ensure that all of the fields are there.
        payload = {
            'title': 'Sample Recipe title',
            'link':'https://example.com/OldRecipe.pdf',
            'description': 'Sample Description',
            'time_minutes':10,
            'price': Decimal('2.5')
        }

        url = detail_url(recipe.id)

        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        recipe.refresh_from_db()

        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)

        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self):
        """Test the deletion of a recipe"""

        recipe = create_recipe(user = self.user)

        url = detail_url(recipe.id)

        # returns a 204 response.
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        # Should return false.
        self.assertFalse(Recipe.objects.filter(id = recipe.id).exists())

    def test_update_user_returns_error(self):
        """Test changing the recipe user results in an error"""
        new_user = create_user(email = 'user2@example.com', password ='test123')
        recipe = create_recipe(user = self.user)

        # remember that all things are tracked via id. That means that just
        # the user id is assigned to them.
        payload = {'user': new_user.id}

        url = detail_url(recipe.id)

        self.client.patch(url, payload)

        recipe.refresh_from_db()

        self.assertEqual(recipe.user, self.user)


    def test_recipe_other_users_recipe_error(self):
        """Test that users are not able to delete other user's recipes"""

        # Create a recipe under this new user
        new_user = create_user(email = 'user3@example.com', password = 'test1235')
        recipe = create_recipe(user = new_user)

        # try to delete another users recipe while logged in as the setup user.
        url = detail_url(recipe.id)
        res = self.client.delete(url)

        # exists only works at the query set level, can't be used on the model level
        # ensure that the error code is generated.
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())

    def test_create_recipe_with_new_tags(self):
        """Create a recipe with new tags"""

        payload={
            'title':'Thai Prawn Curry',
            'time_minutes':30,
            'price': Decimal('2.5'),
            'tags':[{'name':'Dinner'}, {'name':'Thai'}]
        }

        # anytime that you are providing nested objects, its best to pass
        # the format as json
        res = self.client.post(RECIPE_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        # count will tell you the number of occurences in the queryset
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)

        # when you are checking that an object is associated with the output
        # the best way is to loop over the payload and then filter the queryset to
        # see if that item exists.
        for tag in payload['tags']:
            exists = recipe.tags.filter(name = tag['name'], user = self.user).exists()
            self.assertTrue(exists)

    def test_create_with_existing_tags(self):
        """Test creating a recipe with existing tags"""

        tag_indian = Tag.objects.create(user = self.user, name='indian')
        payload = {
            'title':'Pongal',
            'time_minutes': 60,
            'price':Decimal('6.60'),
            'tags':[{'name':'indian'}, {'name':'vegetarian'}]
        }

        res = self.client.post(RECIPE_URL, payload, format='json')

        # We would expect there to be two tags at the end.
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user = self.user)
        self.assertEqual(recipes.count(), 1)  # Check that only 1 recipe was created
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)  # check that both tags were assgined.
        # Notice we are looking to see if the tag is present in the recipe tags objects.
        # It looks here that selecting a particular object from the query object will return a
        # object rather than another query.

        # here you are checking if an object is in a queryset. Iterable of objects.
        self.assertIn(tag_indian, recipe.tags.all())  # all returns a queryset of objects.
        # Here you are actually checking that the exact model that you created earlier is being used,
        # not another version of the indian tag.

        for tag in payload['tags']:
            exists = recipe.tags.filter(name = tag['name'], user = self.user).exists()
            self.assertTrue(exists)

    def test_create_tag_on_update(self):
        """Make sure that a tag is also created when a tag is created."""
        recipe = create_recipe(user = self.user)

        payload = {'tags': [{'name':'American'}]}

        url= detail_url(recipe.id)

        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Rather than checking that the tag was set to the payload, we are
        # pulling that tag id from the db to ensure that it was created as
        # well.
        new_tag = Tag.objects.get(user=self.user, name='American')
        # Don't need to referesh from db on a many to many fields.
        self.assertIn(new_tag, recipe.tags.all())

    def test_update_recipe_assign_tags(self):
        """Test that tags are assigned when updating a recipe"""

        # Create tag
        tag_breakfast = Tag.objects.create(name = 'Breakfast', user = self.user)
        # Create recipe
        recipe = create_recipe(user = self.user)
        # Add tag to recipe. on foreign keys it looks like you can just add it.
        recipe.tags.add(tag_breakfast)

        tag_lunch = Tag.objects.create(name='Lunch', user = self.user)

        # Update recipe with tag
        url = detail_url(recipe.id)
        payload = {'tags':[{'name':'Lunch'}]}
        res = self.client.patch(url, payload, format='json')

        # assertions
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag_lunch, recipe.tags.all())

        # Notice that we are overwriting the tags field, we aren't appending.
        # so that means that we should see the breakfast tag get swapped out.
        self.assertNotIn(tag_breakfast, recipe.tags.all())


    def test_clear_recipe_tags(self):
        """Test clearing out a recipe's tags"""

        tag = Tag.objects.create(user = self.user, name = "Dessert")
        recipe = create_recipe(user = self.user)
        recipe.tags.add(tag)

        payload = {'tags': []}

        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')


        # notice that we aren't serializing because we are just checking the
        # db directly with the objects that we had assigned earlier.
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tags.count(), 0)

    def test_create_recipe_with_new_ingredients(self):
            """Test creating a receipe with new ingredients"""

            payload = {
                'title': 'Califlower Tacos',
                'time_minutes': 60,
                'price': Decimal('4.30'),
                'ingredients':[{'name':'Califlower'},{'name':'Salt'}]
            }

            res = self.client.post(RECIPE_URL, payload, format='json')

            self.assertEqual(res.status_code, status.HTTP_201_CREATED)
            recipes = Recipe.objects.filter(user = self.user)
            self.assertEqual(recipes.count(),1)
            recipe = recipes[0]
            self.assertEqual(recipe.ingredients.count(), 2)
            for ingredient in payload['ingredients']:
                exists = recipe.ingredients.filter(name=ingredient['name'], user=self.user).exists()
                self.assertTrue(exists)


    def test_create_recipe_with_existing_ingredient(self):
        """test creating a recipe with an ingredient that already exists"""
        ingredient = Ingredient.objects.create(name ='lemon', user=self.user)
        payload = {
            'title': 'vietnamese soup',
            'time_minutes' : 25,
            'price': '2.4',
            'ingredients':[{'name':'fish'}, {'name':'lemon'},{'name':'basil'}]
        }

        res = self.client.post(RECIPE_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user = self.user)
        self.assertEqual(recipes.count(),1)
        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(),3)
        # Here we are checking that the same object that we created is present in the recipe.
        # We want to make sure that we aren't creating a second one.
        self.assertIn(ingredient, recipe.ingredients.all())

        # Then we need to make sure that the remainder of the ingredients are present.
        for ingredient in payload['ingredients']:
            exists = recipe.ingredients.filter(
                name=ingredient['name'],
                user = self.user
                ).exists()
            self.assertTrue(exists)


    def test_create_ingredient_on_update(self):
        """Test that you are able to create an ingredient while updating a recipe"""

        recipe = create_recipe(self.user)

        payload = {'ingredients': [{'name':'banana'}]}

        url = detail_url(recipe.id)

        res = self.client.patch(url, payload, format = 'json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        recipe.refresh_from_db()

        for ingredient in payload['ingredients']:
            exists = recipe.ingredients.filter(name = ingredient['name']).exists()
            self.assertTrue(exists)

    def test_assign_ingredient_on_update(self):
        """Test that you are able to assign ingredients on update."""
        ingredient = Ingredient.objects.create(name='lemon', user = self.user)
        recipe =  create_recipe(user = self.user) # by default this does not have ingred.

        url = detail_url(recipe.id) # we use this in case we change any of the urls. dynamic

        payload = {'ingredients':[{'name':'lemon'}]}

        res = self.client.patch(url, payload, format='json' )

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertIn(ingredient, recipe.ingredients.all())

    def test_overwrite_ingredient_on_update(self):
        """Test that you are able to overwrite ingredients on update."""
        ingredient1 = Ingredient.objects.create(name='lemon', user = self.user)
        recipe =  create_recipe(user = self.user) # by default this does not have ingred.
        recipe.ingredients.add(ingredient1)

        ingredient2 = Ingredient.objects.create(name='lime', user = self.user)
        payload = {'ingredients':[{'name':'lime'}]}
        url = detail_url(recipe.id) # we use this in case we change any of the urls. dynamic
        res = self.client.patch(url, payload, format='json' )

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertIn(ingredient1, recipe.ingredients.all())
        self.assertNotIn(ingredient2, recipe.ingredients.all())


    def test_overwrite_ingredient_on_update(self):
        """Test that you are able to clear ingredients on update."""
        ingredient = Ingredient.objects.create(name='lemon', user = self.user)
        recipe =  create_recipe(user = self.user) # by default this does not have ingred.
        recipe.ingredients.add(ingredient)

        payload = {'ingredients':[]}
        url = detail_url(recipe.id) # we use this in case we change any of the urls. dynamic
        res = self.client.patch(url, payload, format='json' )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertNotIn(ingredient, recipe.ingredients.all())
        self.assertEqual(recipe.ingredients.count(),0)


