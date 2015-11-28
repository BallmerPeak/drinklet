from django.db import models
from django.db.utils import IntegrityError
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

    def get_ingredients(self):
        ret_dict = {}
        recipe_ingredients = self.recipeingredients_set.select_related('ingredient')

        for recipe_ingredient in recipe_ingredients:
            ret_dict[recipe_ingredient.ingredient.id] = recipe_ingredient.quantity

        return ret_dict

    def edit_recipe(self, recipe_name, instructions, ingredients):
        new_ingredients = []
        recipe_ingredients = []
        if self.name != recipe_name.lower():
            if Recipe.objects.filter(name=recipe_name.lower()).exists():
                raise IntegrityError('Recipe with name: {} already exists!'.format(recipe_name))

            self.name = recipe_name.lower()

        if not instructions or not ingredients:
            raise ValueError('One or both of instruction and ingredients are empty!')

        self.instructions_blob = '~~~'.join(instructions)

        if ingredients != self.get_ingredients():
            for key, info in ingredients.items():
                if isinstance(key, str):
                    category, quantity, uom = info
                    new_ingredients.append((key, category, quantity, uom))
                else:
                    recipe_ingredients.append((key, info))

            recipe_ingredients += Ingredient._create_ingredient_objs(new_ingredients)
            self.recipeingredients_set.all().delete()

            RecipeIngredients._add_ingredients(self, recipe_ingredients)
        self.save()
        self.refresh_from_db()

        return self

    def add_user_stats(self, user_ingredients):
        from recipes.helper_objects import RecipeInfo
        recipe_info = RecipeInfo(self, user_ingredients)
        self.num_can_make = recipe_info.num_can_make
        self.missing_ingredients = recipe_info.missing_ingredients

    @classmethod
    def get_recipes_by_ingredients(cls, ingredient_ids, user_ingredients=None):
        found_recipes = []
        ingredients = frozenset(ingredient_ids)
        recipes = cls.objects.filter(ingredients__id__in=ingredients).distinct().prefetch_related('ingredients')

        for recipe in recipes:
            recipe_ingredients = [x.id for x in list(recipe.ingredients.all())]
            if ingredients.issuperset(recipe_ingredients):
                if user_ingredients:
                    recipe.add_user_stats(user_ingredients)
                found_recipes.append(recipe)

        return found_recipes

    @classmethod
    def get_all_recipes(cls):
        queryset = RecipeIngredients.objects.select_related('ingredient')
        return cls.objects.prefetch_related(models.Prefetch('recipeingredients_set', queryset=queryset))

    @classmethod
    def _get_recipes_with_user_stats(cls, user_ingredients):

        return cls._add_user_stats_to_collection(Recipe.objects.all(), user_ingredients)

    @classmethod
    def _add_recipe(cls, name, instructions, ingredients):
        blob_instructions = '~~~'.join(instructions)
        recipe = cls(name=name.lower(),
                     instructions_blob=blob_instructions)
        recipe.save()
        RecipeIngredients._add_ingredients(recipe, ingredients)
        return recipe

    def _delete_recipe(self):
        self.delete()

    @classmethod
    def _add_user_stats_to_collection(cls, recipes, user_ingredients):
        queryset = RecipeIngredients.objects.select_related('ingredient')
        recipes = recipes.prefetch_related(models.Prefetch('recipeingredients_set', queryset=queryset))

        for recipe in recipes:
            recipe.add_user_stats(user_ingredients)

        return recipes


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
