from django.db import models
from django.conf import settings
from recipes.models import Recipe
from ingredients.models import Ingredient
from django.core.validators import MaxValueValidator

# Create your models here.


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, primary_key=True)
    favorites = models.ManyToManyField(Recipe)
    recipe_ratings = models.ManyToManyField(Recipe, through='UserRecipeRating', related_name='user_ratings')
    ingredients = models.ManyToManyField(Ingredient, through='UserIngredients', related_name='user_ingredients')
    created_recipes = models.ManyToManyField(Recipe, through='UserCreatedRecipes', related_name='user_created_recipes')

    @classmethod
    def create_or_get_profile(cls, user):
        profile, _ = cls.objects.get_or_create(user=user)
        return profile

    def set_favorites(self, recipe_id):
        favorite = Recipe.objects.get(id=recipe_id)
        self.favorites.add(favorite)

    def get_favorites(self):
        return self.favorites

    def set_rating(self, recipe_id, rating):

        UserRecipeRating._set_rating(self, recipe_id, rating)
        recipe_ratings = UserRecipeRating.objects.filter(user=self)

        return self._create_dict(recipe_ratings, 'recipe_id', 'rating')

    def add_user_ingredients(self, ingredient_ids):
        UserIngredients._add_user_ingredients(self, ingredient_ids)
        user_ingredients = UserIngredients.objects.filter(user=self)

        return self._create_dict(user_ingredients, 'ingredient_id', 'quantity')

    def delete_user_ingredient(self, ingredient_id):
        UserIngredients._delete_user_ingredient(self, ingredient_id)
        user_ingredients = UserIngredients.objects.filter(user=self)

        return self._create_dict(user_ingredients, 'ingredient_id', 'quantity')

    @staticmethod
    def _create_dict(obj_list, rel_key, rel_value):
        ret = {}

        for obj in obj_list:
            ret[getattr(obj, rel_key)] = getattr(obj, rel_value)

        return ret


class UserRecipeRating(models.Model):
    user = models.ForeignKey(UserProfile)
    recipe = models.ForeignKey(Recipe)
    rating = models.PositiveSmallIntegerField(validators=[MaxValueValidator(5)], default=0)

    @classmethod
    def _set_rating(cls, user, recipe_id, rating):
        recipe = Recipe.objects.get(id=recipe_id)
        recipe_rating, created = cls.objects.get_or_create(user=user, recipe=recipe)

        if created:
            recipe.ratings_sum += rating
            recipe.total_ratings += 1

        else:
            recipe.ratings_sum = recipe.ratings_sum - recipe_rating.rating + rating

        recipe_rating.rating = rating
        recipe_rating.save()
        recipe.save()


class UserIngredients(models.Model):
    user = models.ForeignKey(UserProfile)
    ingredient = models.ForeignKey(Ingredient)
    quantity = models.PositiveIntegerField(default=0)

    @classmethod
    def _add_user_ingredients(cls, user, ingredient_ids):
        ingredients = list(Ingredient.objects.in_bulk(ingredient_ids).values())
        user_ingredients = []
        for ingredient in ingredients:
            user_ingredients.append(UserIngredients(user=user, ingredient=ingredient))

        cls.objects.bulk_create(user_ingredients)

    @classmethod
    def _delete_user_ingredient(cls, user, ingredient_id):
        cls.objects.filter(user=user, ingredient_id=ingredient_id).delete()


class UserCreatedRecipes(models.Model):
    user = models.ForeignKey(UserProfile)
    recipe = models.ForeignKey(Recipe)
