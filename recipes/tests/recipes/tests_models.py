from django.db import transaction
from django.db.utils import IntegrityError
from django.test import TestCase
from django.contrib.auth.models import User
from recipes.models import Recipe
from ingredients.models import Ingredient
from user.models import UserProfile


# Create your tests here.

class RecipeTestCase(TestCase):
    def setUp(self):
        user = User.objects.create_user('testuser')
        profile = UserProfile.get_or_create_profile(user)
        Ingredient.objects.bulk_create([Ingredient(name='vodka', category='alcohol'),
                                        Ingredient(name='rum', category='alcohol'),
                                        Ingredient(name='gin', category='alcohol'),
                                        Ingredient(name='orange juice', category='juice'),
                                        Ingredient(name='pineapple juice', category='juice'),
                                        Ingredient(name='white rum', category='alcohol'),
                                        Ingredient(name='coconut cream', category='milk')])

        self.vodka_id = Ingredient.objects.get(name='vodka').id
        self.oj_id = Ingredient.objects.get(name='orange juice').id
        self.gin_id = Ingredient.objects.get(name='gin').id
        self.rum_id = Ingredient.objects.get(name='rum').id
        self.pineapple_juice_id = Ingredient.objects.get(name='pineapple juice').id
        self.white_rum_id = Ingredient.objects.get(name='white rum').id
        self.coconut_cream_id = Ingredient.objects.get(name='coconut cream').id

        screwdriver_recipe_info = (
            'Screwdriver',
            [
                'Fill glass with ice',
                'Add 2 parts Orange Juice',
                'Add 1 part Vodka',
                'Shake well'
            ],
            {
                self.vodka_id: 1,
                self.oj_id: 2
            }
        )

        gin_vodka_recipe_info = (
            'Gin and Vodka',
            [
                'Add 1 part Gin',
                'Add 1 part Vodka',
                'Enjoy!'
            ],
            {
                self.vodka_id: 1,
                self.gin_id: 1
            }
        )

        pina_colada_recipe_info = (
            'Pina Colada',
            [
                'Add 3 parts pineapple juice',
                'Add 1 part white rum',
                'Add 1 part coconut cream',
                'Mixed with crushed ice until smooth',
                'Pour into chilled glass'
            ],
            {
                self.pineapple_juice_id: 3,
                self.white_rum_id: 1,
                self.coconut_cream_id: 1
            }
        )

        profile.create_recipe(*pina_colada_recipe_info)
        profile.create_recipe(*gin_vodka_recipe_info)
        profile.create_recipe(*screwdriver_recipe_info)
        self.screwdriver = Recipe.objects.get(name='screwdriver')
        self.gin_vodka = Recipe.objects.get(name='gin and vodka')
        self.pina_colada = Recipe.objects.get(name='pina colada')

    def test_get_recipes_by_ingredients(self):
        # Test get Pina Colada
        def get_one_drink():
            recipes = Recipe.get_recipes_by_ingredients([self.pineapple_juice_id,
                                                         self.white_rum_id,
                                                         self.coconut_cream_id])
            self.assertEqual(1, len(recipes))
            self.assertEqual(self.pina_colada, recipes[0])

        # Test get Screwdriver and gin and vodka
        def get_two_drinks():
            recipes = Recipe.get_recipes_by_ingredients([self.vodka_id,
                                                         self.gin_id,
                                                         self.oj_id])
            recipes.sort(key=lambda recipe: recipe.id)
            expected_recipes = sorted([self.gin_vodka, self.screwdriver], key=lambda recipe: recipe.id)
            self.assertEqual(2, len(recipes))
            self.assertListEqual(expected_recipes, recipes)

        # Test get only Screwdriver with more than 2 ingredients
        def get_one_drink_with_extra_ingredients():
            recipes = Recipe.get_recipes_by_ingredients([self.vodka_id,
                                                         self.pineapple_juice_id,
                                                         self.oj_id,
                                                         self.rum_id])
            self.assertEqual(1, len(recipes))
            self.assertEqual(self.screwdriver, recipes[0])

        # Test Get all 3 recipes using all ingredients
        def get_drinks_with_all_ingredients():
            recipes = Recipe.get_recipes_by_ingredients([self.coconut_cream_id,
                                                         self.pineapple_juice_id,
                                                         self.gin_id,
                                                         self.oj_id,
                                                         self.vodka_id,
                                                         self.rum_id,
                                                         self.white_rum_id])
            recipes.sort(key=lambda recipe: recipe.id)
            expected_recipes = sorted([self.gin_vodka, self.screwdriver, self.pina_colada], key=lambda recipe: recipe.id)
            self.assertEqual(3, len(recipes))
            self.assertListEqual(expected_recipes, recipes)

        get_one_drink()
        get_two_drinks()
        get_one_drink_with_extra_ingredients()
        get_drinks_with_all_ingredients()

    def test_edit_recipe(self):

        def change_recipe_name():
            args = ('Pina Molada', self.pina_colada.get_instructions(), self.pina_colada.get_ingredients())
            edited_recipe = self.pina_colada.edit_recipe(*args)

            self.assertEqual(self.pina_colada.id, edited_recipe.id)
            self.assertEqual('pina molada', edited_recipe.name)

            self.pina_colada.refresh_from_db()
            self.assertEqual(edited_recipe, self.pina_colada)

        def change_recipe_name_to_existing_name():
            args = ('Screwdriver', self.pina_colada.get_instructions(), self.pina_colada.get_ingredients())

            with self.assertRaises(IntegrityError):
                with transaction.atomic():
                    self.pina_colada.edit_recipe(*args)

        def add_one_existing_ingredient():
            ingredients = self.pina_colada.get_ingredients()
            ingredients.update({
                self.oj_id: 2
            })

            args = (self.pina_colada.name, self.pina_colada.get_instructions(), ingredients)

            edited_recipe = self.pina_colada.edit_recipe(*args)
            self.assertEqual(self.pina_colada.id, edited_recipe.id)
            self.assertDictEqual(ingredients, edited_recipe.get_ingredients())

            self.pina_colada.refresh_from_db()
            self.assertEqual(edited_recipe, self.pina_colada)

        def add_one_new_ingredient():
            ingredients = self.pina_colada.get_ingredients()
            ingredients.update({
                'new ingredient': ('alcohol', 3, 'oz')
            })

            args = (self.pina_colada.name, self.pina_colada.get_instructions(), ingredients)

            edited_recipe = self.pina_colada.edit_recipe(*args)

            del ingredients['new ingredient']
            new_ingredient_id = Ingredient.objects.get(name='new ingredient').id
            ingredients[new_ingredient_id] = 3

            self.assertEqual(self.pina_colada.id, edited_recipe.id)
            self.assertDictEqual(ingredients, edited_recipe.get_ingredients())

            self.pina_colada.refresh_from_db()
            self.assertEqual(edited_recipe, self.pina_colada)

        def remove_one_ingredient():
            ingredients = self.pina_colada.get_ingredients()
            old_count = len(ingredients)
            ingredients.popitem()

            self.assertEqual(old_count - 1, len(ingredients))

            args = (self.pina_colada.name, self.pina_colada.get_instructions(), ingredients)

            edited_recipe = self.pina_colada.edit_recipe(*args)

            self.assertEqual(self.pina_colada.id, edited_recipe.id)
            self.assertDictEqual(ingredients, edited_recipe.get_ingredients())

            self.pina_colada.refresh_from_db()
            self.assertEqual(edited_recipe, self.pina_colada)

        def remove_all_ingredients():
            ingredients = {}

            args = (self.pina_colada.name, self.pina_colada.get_instructions(), ingredients)

            with self.assertRaises(ValueError):
                with transaction.atomic():
                    self.pina_colada.edit_recipe(*args)

        def add_one_instruction():
            instructions = self.pina_colada.get_instructions()
            instructions.append('A new instruction')

            args = (self.pina_colada.name, instructions, self.pina_colada.get_ingredients())

            edited_recipe = self.pina_colada.edit_recipe(*args)

            self.assertEqual(self.pina_colada.id, edited_recipe.id)
            self.assertListEqual(instructions, edited_recipe.get_instructions())

            self.pina_colada.refresh_from_db()
            self.assertEqual(edited_recipe, self.pina_colada)

        def remove_one_instruction():
            instructions = self.pina_colada.get_instructions()
            old_count = len(instructions)
            instructions.pop()

            self.assertEqual(old_count - 1, len(instructions))
            args = (self.pina_colada.name, instructions, self.pina_colada.get_ingredients())
            edited_recipe = self.pina_colada.edit_recipe(*args)

            self.assertEqual(self.pina_colada.id, edited_recipe.id)
            self.assertListEqual(instructions, edited_recipe.get_instructions())

            self.pina_colada.refresh_from_db()
            self.assertEqual(edited_recipe, self.pina_colada)

        def remove_all_instructions():
            instructions = []

            args = (self.pina_colada.name, instructions, self.pina_colada.get_ingredients())

            with self.assertRaises(ValueError):
                with transaction.atomic():
                    self.pina_colada.edit_recipe(*args)

        change_recipe_name()
        change_recipe_name_to_existing_name()
        add_one_existing_ingredient()
        add_one_new_ingredient()
        remove_one_ingredient()
        remove_all_ingredients()
        add_one_instruction()
        remove_one_instruction()
        remove_all_instructions()

    def test_get_all_recipes(self):
        recipes = Recipe.get_all_recipes()
        self.assertEqual(3, recipes.count())

        expected_recipes = sorted([self.pina_colada, self.screwdriver, self.gin_vodka], key=lambda recipe: recipe.id)

        self.assertListEqual(expected_recipes, list(recipes))



