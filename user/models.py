from django.db import models
from django.conf import settings
from recipes.models import Recipe
from ingredients.models import Ingredient
from django.core.validators import MaxValueValidator

# Create your models here.


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, primary_key=True)
    favorites = models.ManyToManyField(Recipe, through='UserFavorite', related_name='user_favorites')
    recipe_ratings = models.ManyToManyField(Recipe, through='UserRecipeRating', related_name='user_ratings')
    ingredients = models.ManyToManyField(Ingredient, through='UserIngredients', related_name='user_ingredients')
    created_recipes = models.ManyToManyField(Recipe, through='UserCreatedRecipes', related_name='user_created_recipes')

    @classmethod
    def create_or_get_profile(cls, user):
        profile, _ = cls.objects.get_or_create(user=user)
        return profile

    def set_favorites(self, recipe_id):
        UserFavorite.__set_favorites(self, recipe_id)


class UserFavorite(models.Model):
    user = models.ForeignKey(UserProfile)
    recipe = models.ForeignKey(Recipe)

    @classmethod
    def __set_favorites(cls, user, recipe_id):
        cls.recipe = Recipe.objects.get(id=recipe_id)
        cls.user = user
        cls.save()

    @classmethod
    def __get_favorites(cls, user_id):
        """
        get_favorites:
        Parameters: User
        Returns: List of recipe objects

        :return:
        """
        pass


class UserRecipeRating(models.Model):
    user = models.ForeignKey(UserProfile)
    recipe = models.ForeignKey(Recipe)
    rating = models.PositiveSmallIntegerField(validators=[MaxValueValidator(5)])

    @classmethod
    def set_rating(cls, user_id, recipe_id, rating):
        """
        set_rating:
        Parameters: rating, user, recipe id
        Dictionary:
        Key - recipe id
        value - user rating

        :return:
        """
        pass


class UserIngredients(models.Model):
    user = models.ForeignKey(UserProfile)
    ingredient = models.ForeignKey(Ingredient)
    quantity = models.PositiveIntegerField()

    @classmethod
    def add_user_ingredients(cls, user_id, ingredient_ids):
        """
        add_user_ingredients:
        Parameters: user, list of ingredient ids
        Returns: Dictionary:
        Key - Ingredient ids
        Value - Quantities

        :return:
        """
        pass

    @classmethod
    def delete_user_ingredient(cls, user_id, ingredient_id):
        """
        delete_user_ingredient:
        Parameters: user, ingredient id
        Returns: Dictionary:
        Key - Ingredient ids
        Value - Quantities

        :return:
        """
        pass


class UserCreatedRecipes(models.Model):
    user = models.ForeignKey(UserProfile)
    recipe = models.ForeignKey(Recipe)
