"""Contains the recipe Serializer"""

from rest_framework import serializers
from core.models import Recipe


class RecipeSerializer(serializers.ModelSerializer):
    """Contains the serializers for the recipe model"""

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'price']
        read_only_fields = ['id']


class RecipeDetailSerializer(RecipeSerializer):
    """Serlizer for recipe detail view, extention of recipe serializer"""

    # Here we are passing the meta class off of the inhereted serializers
    # meta class. Pass in all of the fields.
    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']