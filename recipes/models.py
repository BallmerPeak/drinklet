from django.db import models
from django.conf import settings
from ingredients.models import Ingredient
# Create your models here.


class Recipe(models.Model):
    name = models.CharField(max_length=30)
    ratings_sum = models.PositiveIntegerField()
    total_ratings = models.PositiveIntegerField()
    instructions = models.CharField(max_length=1000)


class RecipeIngredients(models.Model):
    recipe = models.ForeignKey(Recipe)
    ingredient = models.ForeignKey(Ingredient)
    quantity = models.PositiveSmallIntegerField()


class RecipeComment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    recipe = models.ForeignKey(Recipe)
    comment_text = models.CharField(max_length=500)
