from rest_framework.viewsets import ModelViewSet
from rest_framework import viewsets, mixins  #?
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe  # Why is the model here?
from core.models import Tag
from core.models import Ingredient
from recipe import serializers

# I forgot to pull in the authentication information. When you authenticate,
# it is going to be be done here at the view level.

class RecipeViewSet(ModelViewSet):
    """Contains the View set for Recipes CRUD operations.
    It should only return recipes that the user owns"""


    # here we are controling what

    # here we are setting a default serializer class.
    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all()  # You point the serializer to the
    # model that will makeup its queryset.
    authentication_classes = [TokenAuthentication]  # ensures type
    permission_classes = [IsAuthenticated]  # ensures is auth.


    def get_queryset(self):
        # Normally it would return everything, we would like that fitlered.
        # Get queryset is how you reduce what is going to be shown
        return self.queryset.filter(user = self.request.user).order_by('-id')

    def get_serializer_class(self):
        """We would like to override which serializer is used depending on the
        endpoint. In this case, remember that there are 2 enpoints, list
        and detail. So whenever we are using the detail we would like to
        use the detail serializer."""

        # switch the serializer class if the action is list.
        # this is the mapping that the router will use, it is essentially
        # the url endpoint. Remeber that if we would like to define our
        # own users then we need to decorate them with the @action.
        # So self.action is how you determine the "URL" in the serializer.
        if self.action == 'list':
            return serializers.RecipeSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Runs when a new recipe is created."""
        # When something is created through this model viewset, then we are
        # going to call this method, it accepts 1 method, the validated
        # serialzer. Then we are able to save the user that is currenlty
        # authenticated to the serializer before pulling it into the model.
        serializer.save(user = self.request.user)


# Why are we using the mixins here and not model viewset? the rest of the code is the same.
# woah the model mixins allow for you to control what can be updated and created. This is just a
# permisison mixin. I assume the model mixin gives it all to you.
class TagViewSet(mixins.DestroyModelMixin,
                 mixins.UpdateModelMixin,
                 mixins.ListModelMixin,
                 viewsets.GenericViewSet):
    """This is the viewset for the tag serializer"""

    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """overwrite the default get query set method. filter for the user (class attribute)
        Then order by the name (alphabetical)"""
        # Don't include the .objects. here. The queryset doesn't have that. Its not the
        # model manager. Also look at the queryset level. This is already at the obj lev.
        return self.queryset.filter(user=self.request.user).order_by('-name')

class IngredientViewset(mixins.DestroyModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.ListModelMixin,
                        viewsets.GenericViewSet):
    """Manage ingredients in the database"""
    serializer_class = serializers.IngredientSerializer
    # Tells django which models we would like to be changed via this view.
    queryset = Ingredient.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter queryset to only the authenticated user"""
        return self.queryset.filter(user = self.request.user).order_by('-name')
