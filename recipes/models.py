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

    def get_instructions(self):
        return self.instructions_blob.split('~~~')

    def edit_recipe(self, recipe_name, instructions, ingredients):
        new_ingredients = []
        recipe_ingredients = []

        self.name = recipe_name
        self.instructions_blob = instructions

        for key, info in ingredients.items():
            if isinstance(key, str):
                category, quantity, uom = info
                new_ingredients.append((key, category, quantity, uom))
            else:
                recipe_ingredients.append((key, info))

        recipe_ingredients += Ingredient._create_ingredient_objs(new_ingredients)
        self.ingredients.clear()

        RecipeIngredients._add_ingredients(self, recipe_ingredients)
        self.save()
        self.refresh_from_db()

        return self

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
    def _add_recipe(cls, name, instructions, ingredients):
        blob_instructions = '~~~'.join(instructions)
        recipe = cls(name=name,
                     instructions_blob=blob_instructions)
        recipe.save()
        RecipeIngredients._add_ingredients(recipe, ingredients)
        return recipe

    def _delete_recipe(self):
        self.delete()


class RecipeIngredients(models.Model):
    recipe = models.ForeignKey(Recipe)
    ingredient = models.ForeignKey(Ingredient)
    quantity = models.DecimalField(default=0, decimal_places=2, max_digits=4)

    def __str__(self):
        return 'Recipe:{recipe} -> Ingredient:{ingredient} -> Quantity:{qty}'.format(recipe=self.recipe,
                                                                                     ingredient=self.ingredient,
                                                                                     qty=self.quantity)

    @classmethod
    def _add_ingredients(cls, recipe, ingredients):
        recipe_ingredients = []

        for ingredient_id, quantity in ingredients:
            recipe_ingredients.append(cls(recipe=recipe,
                                          ingredient_id=ingredient_id,
                                          quantity=quantity))

        cls.objects.bulk_create(recipe_ingredients)
