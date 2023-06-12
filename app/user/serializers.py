"""Serializers for the user API view"""

from django.contrib.auth import (
    get_user_model,
    authenticate,
    )
from django.utils.translation import gettext as _  # Industry Norm

# Takes input, validates input, converts to a python object/model M here
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""

    # Remember that all serializers need this meta class that tells them
    # which model they are responsible for serializing.
    class Meta:
        model = get_user_model()
        # Fields that are going to be provided in the request that needs vali.
        # Don't include anything that can't be set! like is_staff.
        fields = ['email', 'password', 'name']
        # These are the extra comments were we require a min len.
        extra_kwargs = {'password': {'write_only': True, 'min_length': 8}}

    # Here we are overriding the default behavior of the serializer.
    # Normally it just stores things as plain text. Here we are hashing
    # The password. Remember that this happens in our create user m.
    # So we only write that hashing code once and force evasive paths
    # Create is only called if the validation passes successfully
    def create(self, validated_data):
        """Create and return a user with an encrypted password"""
        return get_user_model().objects.create_user(**validated_data)

    # Override the default functionality. Passwords need to be hashed.
    def update(self, instance, validated_data):
        """This allows for the updating of the user profile data."""

        # Remove the password, then use the inherited update method.
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        # Then take the password that is popped and hash it and save.
        if password:
            user.set_password(password)
            user.save()

        return user

class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user auth token"""
    # Becuase a token is not a model, we are not using ModelSerial.

    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace = False
    )

    def validate(self, attrs):
        """Validate the user that is logging in"""
        email = attrs.get('email')
        password = attrs.get('password')

        # Context is the dict of values required to host the session.
        # I wonder why this is required to authenticate. Do you need to val
        # users on a session by session basis?
        # Remember that the user is always included in the context manager.

        user = authenticate(
            request=self.context.get('request'),
            username = email,
            password = password
        )

        # What you want the api to put out if the user is not validated
        if not user:
            # The get text function allows us to display messages.
            msg = _('unable to authenticate with provided credentials')
            # return a 400 response
            raise serializers.ValidationError(msg, code='authorization')

        # Assign the user to the input dictionary and rereturn it.
        attrs['user'] = user

        return attrs
