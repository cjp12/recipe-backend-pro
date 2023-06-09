"""Database Models"""

from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)


class UserManager(BaseUserManager):
    """Manager for users. Used to create users."""

    def create_user(self, email, password=None, **extra_fields):
        """Create, save, and return a new user"""

        # Throw an error if the user doesn't have an email.
        if not email:
            raise ValueError('User mst have an email address')

        # Creates a user with the minimum criteria, U and P
        # Because of the objects assignment, self.model is suff
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)  # set = hashing
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Create and return a new superuser"""

        # Remember that you have to use self because it is a diff method.
        # Able to leverage the create user method to save time on code.
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)  # Don't forget to save

        return user

class User(AbstractBaseUser, PermissionsMixin):
    """Custom users for the system."""

    # Here we set up our model criteria
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # Assign this model to the User Manager class
    objects = UserManager()

    # This is how we make the default username into the email
    USERNAME_FIELD = 'email'
