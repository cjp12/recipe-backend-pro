"""URL mappings for recipe"""

from django.urls import path
from django.urls import include

from rest_framework.routers import DefaultRouter

from recipe import views

router = DefaultRouter()

# here you are mapping recipes to the recipe viewset.
# These will be the outward facing urls. These will be seen on the endpoint.
# The model name is used to
router.register('recipes', views.RecipeViewSet)
router.register('tags', views.TagViewSet)
router.register('ingredients', views.IngredientViewset)

# Used for the reverse lookup of urls
app_name='recipe'


urlpatterns=[
    path('', include(router.urls)),
]