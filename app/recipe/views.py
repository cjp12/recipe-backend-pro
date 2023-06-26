from rest_framework.viewsets import ModelViewSet
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe  # Why is the model here?
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