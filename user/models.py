from django.db import models
from django.conf import settings
from recipes.models import Recipe
from ingredients.models import Ingredient
from django.core.validators import MaxValueValidator

# Create your models here.


class UserFavorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    recipe = models.ForeignKey(Recipe)


class UserRecipeRating(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    recipe = models.ForeignKey(Recipe)
    rating = models.PositiveSmallIntegerField(validators=[MaxValueValidator(5)])


class UserIngredients(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    ingredient = models.ForeignKey(Ingredient)
    quantity = models.PositiveIntegerField()
