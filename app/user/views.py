"""views for the user api"""

# generics contains many of the base classes to speed up development.
from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from user.serializers import (
    UserSerializer,
    AuthTokenSerializer
)

# Here it looks like we are creating a form.
# CreateAPIView takes a POST request.
# by looking at the serializer, it can then tie it to a model.
# Used to create!
class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system"""
    serializer_class=UserSerializer

# RetrieveUpdateAPI view is used to r/u items in the database.
# It takes get and patch methods.
class ManageUserView(generics.RetrieveUpdateAPIView):
    """Update a user the extra content here enables securty and auth"""
    serializer_class=UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """return the requested user"""
        # This gets run through the serializer before being returned.
        return self.request.user

class CreateTokenView(ObtainAuthToken):
    """Request a token for the user when they log in"""
    serializer_class=AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES