"""Database Models"""

from django.conf import settings
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


class Recipe(models.Model):
    """Stores the recipes"""

    # Here we are setting the foreign key to the user
    # Referenced from the settigns instead of direct imports
    # in case the auth model changes. Not hard coded
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    time_minutes = models.IntegerField()
    link = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    description = models.TextField(blank=True)
    # My first many to many!
    tags = models.ManyToManyField('Tag')  # make sure to pass as a string
    ingredients = models.ManyToManyField('Ingredient')

    # We should be able to skip the objects assignment here because we are
    # adopting the model base class and not creating a custom class

    def __str__(self):
        """returns the title if the object is printed"""
        return self.title


class Tag(models.Model):
    """Tag for filtering recipes"""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Ingredient that will make up the components of a receipe"""
    name = models.CharField(max_length=255)
    # settings.AUTH_USER_MODEL is taken from the settings file that we set.
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.name