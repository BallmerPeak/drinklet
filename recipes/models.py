from django.db import models
from ingredients.models import Ingredient
# Create your models here.


class Recipe(models.Model):
    name = models.CharField(max_length=30, unique=True)
    ratings_sum = models.PositiveIntegerField(default=0)
    num_ratings = models.PositiveIntegerField(default=0)
    instructions_blob = models.CharField(max_length=1000)
    ingredients = models.ManyToManyField(Ingredient, through='RecipeIngredients', related_name='recipe_ingredients')

    def __str__(self):
        return self.name

    @classmethod
    def get_recipes_by_ingredients(cls, ingredient_ids):
        found_recipes = []
        ingredients = frozenset(ingredient_ids)
        recipes = cls.objects.filter(ingredients__id__in=ingredients).distinct().prefetch_related('ingredients')

        for recipe in recipes:
            recipe_ingredients = [x.id for x in list(recipe.ingredients.all())]
            if ingredients.issuperset(recipe_ingredients):
                recipe.instruction = recipe.instructions_blob.split('~~~')
                found_recipes.append(recipe)

        return found_recipes

    @classmethod
    def _add_recipe(cls, name, instructions, ingredients_info):
        blob_instructions = '~~~'.join(instructions)
        recipe = cls(name=name,
                     instructions_blob=blob_instructions)
        recipe.save()
        RecipeIngredients._add_ingredients(recipe, ingredients_info)
        return recipe


class RecipeIngredients(models.Model):
    recipe = models.ForeignKey(Recipe)
    ingredient = models.ForeignKey(Ingredient)
    quantity = models.PositiveSmallIntegerField()

    def __str__(self):
        return 'Recipe:{recipe} -> Ingredient:{ingredient} -> Quantity:{qty}'.format(recipe=self.recipe,
                                                                                     ingredient=self.ingredient,
                                                                                     qty=self.quantity)

    @classmethod
    def _add_ingredients(cls, recipe, ingredients):
        recipe_ingredients = []

        for ingredient_id, quantity in ingredients.items():
            recipe_ingredients.append(cls(recipe=recipe,
                                          ingredient_id=ingredient_id,
                                          quantity=quantity))

        cls.objects.bulk_create(recipe_ingredients)
