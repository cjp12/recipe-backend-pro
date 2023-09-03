"""Contains the recipe Serializer"""

from rest_framework import serializers
from core.models import Recipe, Tag, Ingredient


# Moved above because it is assigned below
class TagSerializer(serializers.ModelSerializer):
    """Serializer used for the Tag model"""

    class Meta:
        model=Tag
        fields = ['id','name']
        read_only_fields = ['id']

class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for the Ingredient Model"""

    class Meta:
        model = Ingredient
        fields = ['id','name']
        read_only_fields = ['id']

class RecipeSerializer(serializers.ModelSerializer):
    """Contains the serializers for the recipe model"""
    # many = list of items
    tags = TagSerializer(many=True, required=False)
    ingredients = IngredientSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'price', 'tags', 'ingredients']
        read_only_fields = ['id']

    def _get_or_create_ingredients(self, ingredients, receipe):
        """Handle the getting or creating of ingredients as needed"""
        auth_user = self.context['request'].user

        for ingredient in ingredients:
            ingredient_obj, created = Ingredient.objects.get_or_create(
                user = auth_user,
                **ingredient # unpack the remainder of the args
            )
            receipe.ingredients.add(ingredient_obj)


    def _get_or_create_tags(self, tags, recipe):
        """Handle getting or creating tags as needed"""
        # get the auth user, serializers use context. views use self.request
        auth_user = self.context['request'].user

    # get or create will get if all fields passed in if all fields passed in match!
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user = auth_user,
                **tag
            )
            recipe.tags.add(tag_obj)

    def create(self, validated_data):
        """Create a recipe, overriding"""
        # idea, pull tags out, create the recipe, get the user, create the tags, add the tags to the recipe, return recipe.

        tags = validated_data.pop('tags', [])  # remove and assign, doesn't exist? default to empty list
        ingredients = validated_data.pop('ingredients', [])

        # Pass in all the other fields that are associated with recipe, not tags
        # Recipe expects a related field, meaning an already created tag.
        recipe = Recipe.objects.create(**validated_data)

        self._get_or_create_tags(tags, recipe)
        self._get_or_create_ingredients(ingredients, recipe)

        return recipe

    def update(self, instance, validated_data):
        """Update recipe"""
        # instance here is the recipe instance that we are updating.
        # pop out the tags. NOT AN EMPTY LIST. EMPTY LIST IS NOT NONE
        tags = validated_data.pop('tags', None)
        ingredients = validated_data.pop('ingredients', None)

        # if they aren't none then we are going to clear out what is already there then assign it.
        if tags is not None:
            instance.tags.clear()  # Clear the tags that were already there
            self._get_or_create_tags(tags, instance)

        if ingredients is not None:
            instance.ingredients.clear()  # Clear the tags that were already there
            self._get_or_create_ingredients(ingredients, instance)

        # This is probably the default language in the update value.
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Save all of the updated instances.
        instance.save()
        return instance

class RecipeDetailSerializer(RecipeSerializer):
    """Serlizer for recipe detail view, extention of recipe serializer"""

    # Here we are passing the meta class off of the inhereted serializers
    # meta class. Pass in all of the fields.
    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']

