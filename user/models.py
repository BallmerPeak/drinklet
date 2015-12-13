from bulk_update.helper import bulk_update
from django.db import models
from django.conf import settings
from django.db.models import ExpressionWrapper, Value, BooleanField, Case, When

from recipes.models import Recipe, RecipeIngredients
from ingredients.models import Ingredient
from django.core.validators import MaxValueValidator
from notifications.tasks import create_notification, remove_orphaned_notifications

# Create your models here.


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, primary_key=True)
    favorites = models.ManyToManyField(Recipe, related_name='user_favorites')
    recipe_ratings = models.ManyToManyField(Recipe, through='UserRecipeRating', related_name='user_ratings')
    ingredients = models.ManyToManyField(Ingredient, through='UserIngredients', related_name='user_ingredients')
    user_recipe_comments = models.ManyToManyField(Recipe, through='RecipeComment', related_name='recipe_comments')

    def __str__(self):
        return self.user.username

    @classmethod
    def get_or_create_profile(cls, user):
        profile, _ = cls.objects.select_related('user').get_or_create(user=user)
        return profile

    def set_favorites(self, recipe_id, is_favorite=None):
        favorite = Recipe.objects.get(id=recipe_id)

        if is_favorite:
            self.favorites.remove(favorite)
            self._remove_orphaned_notifications()
        else:
            self.favorites.add(favorite)
            self._create_user_notification()

        return self.get_favorites()

    def get_favorites(self):
        user_ingredients = self.useringredients_set.select_related('ingredient')
        recipes = self.favorites.annotate(
            is_author=Case(
                When(author=self, then=Value(True)),
                default=Value(False),
                output_field=BooleanField()
            )
        )

        return Recipe._add_user_stats_to_collection(recipes, user_ingredients)

    def get_created_recipes(self):
        user_ingredients = self.useringredients_set.select_related('ingredient')
        created_recipes = self.created_recipes.annotate(
            is_author=ExpressionWrapper(Value(True), output_field=BooleanField()))

        return Recipe._add_user_stats_to_collection(created_recipes, user_ingredients)

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

        self._create_user_notification()

        return self._create_dict(user_ingredients, 'ingredient_id', 'quantity')

    def bulk_update_user_ingredient_quantity(self, user_ingredients):
        bulk_update(user_ingredients, update_fields=['quantity'])

        self._create_user_notification()

    def create_recipe(self, recipe_name, instructions, ingredients):
        new_ingredients = []
        recipe_ingredients = []

        for key, info in ingredients.items():
            if isinstance(key, str):
                category, quantity, uom = info
                new_ingredients.append((key, category, quantity, uom))
            else:
                recipe_ingredients.append((key, info))

        recipe_ingredients += Ingredient._create_ingredient_objs(new_ingredients)

        recipe = Recipe._add_recipe(recipe_name, instructions, recipe_ingredients, self)

        self._create_user_notification()

        return recipe

    def delete_recipe(self, recipe_id):
        recipe = self.created_recipes.get(id=recipe_id)
        recipe._delete_recipe()

        self.refresh_from_db()

        self._remove_orphaned_notifications()

        return self

    def get_all_recipes(self):
        user_ingredients = self.useringredients_set.select_related('ingredient')
        recipes = Recipe.objects.annotate(
            is_author=Case(
                When(author=self, then=Value(True)),
                default=Value(False),
                output_field=BooleanField()
            )
        )
        return Recipe._add_user_stats_to_collection(recipes, user_ingredients)

    def get_recipes_by_ingredients(self, ingredient_ids):
        user_ingredients = self.useringredients_set.select_related('ingredient')
        recipes = Recipe.objects.annotate(
            is_author=Case(
                When(author=self, then=Value(True)),
                default=Value(False),
                output_field=BooleanField()
            )
        )
        return Recipe.get_recipes_by_ingredients(ingredient_ids, user_ingredients, recipes)

    def _create_user_notification(self):
        user_info = {'pk': self.pk}

        try:
            create_notification.delay(user_info)
        except OSError:
            create_notification(user_info)

    def _remove_orphaned_notifications(self):
        user_info = {'pk': self.pk}

        try:
            remove_orphaned_notifications.delay(user_info)
        except OSError:
            remove_orphaned_notifications(user_info)

    # def get_recipe(self, get_filter_dict):
    #     user_ingredients = self.useringredients_set.select_related('ingredient')
    #     recipe = Recipe._get_recipe(get_filter_dict)
    #     recipe._add_user_stats(user_ingredients)
    #
    #     return recipe

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

    def __str__(self):
        return "User:{user} -> Recipe:{recipe} ->  Rating:{rating}".format(user=self.user,
                                                                           recipe=self.recipe, rating=self.rating)

    @classmethod
    def _set_rating(cls, user, recipe_id, rating):
        recipe = Recipe.objects.get(id=recipe_id)
        recipe_rating, created = cls.objects.get_or_create(user=user, recipe=recipe)

        if created:
            recipe.ratings_sum += rating
            recipe.num_ratings += 1

        else:
            recipe.ratings_sum = recipe.ratings_sum - recipe_rating.rating + rating

        recipe_rating.rating = rating
        recipe_rating.save()
        recipe.save()


class UserIngredients(models.Model):
    user = models.ForeignKey(UserProfile)
    ingredient = models.ForeignKey(Ingredient)
    quantity = models.DecimalField(default=0, decimal_places=2, max_digits=8)

    class Meta:
        unique_together = ('user', 'ingredient',)

    def __str__(self):
        return "User:{user} -> Ingredient:{ingredient} -> Quantity:{quantity}".format(user=self.user,
                                                                                      ingredient=self.ingredient,
                                                                                      quantity=self.quantity)

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


class RecipeComment(models.Model):
    user = models.ForeignKey(UserProfile)
    recipe = models.ForeignKey(Recipe)
    comment_text = models.CharField(max_length=500)
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-timestamp']
        unique_together = (('user', 'recipe'),)

    def __str__(self):
        return "Author:{user} -> Recipe:{recipe} -> Comment:({comment})".format(user=self.user, recipe=self.recipe,
                                                                                comment=self.comment_text[:10])
