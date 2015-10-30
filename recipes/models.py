from django.db import models
from ingredients.models import Ingredient
# Create your models here.


class Recipe(models.Model):
    name = models.CharField(max_length=30)
    ratings_sum = models.PositiveIntegerField()
    total_ratings = models.PositiveIntegerField()
    instructions = models.CharField(max_length=1000)

    @classmethod
    def get_recipes_by_ingredients(cls, ingredient_ids):
        """
        get_recipe_by_ingredients:
        Parameters: List of ingredient ids
        Return: List of Tuples (A,B):
        A - Recipe Objects
        B - Recipe Ingredient Objects

        :return:
        """
        pass

    @classmethod
    def add_recipes(cls, recipe_info):
        """
        Parameters: Dictionary:
        {
                                      name: string,
                                      username: string,
                                      instructions: list of strings,
                                      ingredients: {
                                          id: int,
                                          quantity: int
                                      }
                                    }
        Returns: List of recipe objects

        :return:
        """
        pass


class RecipeIngredients(models.Model):
    recipe = models.ForeignKey(Recipe)
    ingredient = models.ForeignKey(Ingredient)
    quantity = models.PositiveSmallIntegerField()

    def __get_recipe_by_ingredient(self):
        pass


class RecipeComment(models.Model):
    user = models.ForeignKey('user.UserProfile')
    recipe = models.ForeignKey(Recipe)
    comment_text = models.CharField(max_length=500)
