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
        Ingredient.objects.bulk_create([Ingredient(name='Vodka', category='alcohol'),
                                        Ingredient(name='Rum', category='alcohol'),
                                        Ingredient(name='Gin', category='alcohol'),
                                        Ingredient(name='Orange Juice', category='juice'),
                                        Ingredient(name='Pineapple Juice', category='juice'),
                                        Ingredient(name='White Rum', category='alcohol'),
                                        Ingredient(name='Coconut Cream', category='milk')])

        self.vodka_id = Ingredient.objects.get(name='Vodka').id
        self.oj_id = Ingredient.objects.get(name='Orange Juice').id
        self.gin_id = Ingredient.objects.get(name='Gin').id
        self.rum_id = Ingredient.objects.get(name='Rum').id
        self.pineapple_juice_id = Ingredient.objects.get(name='Pineapple Juice').id
        self.white_rum_id = Ingredient.objects.get(name='White Rum').id
        self.coconut_cream_id = Ingredient.objects.get(name='Coconut Cream').id

        screwdriver_recipe_info = {
            'name': 'Screwdriver',
            'instructions': [
                'Fill glass with ice',
                'Add 2 parts Orange Juice',
                'Add 1 part Vodka',
                'Shake well'
            ],
            'ingredients': {
                self.vodka_id: 1,
                self.oj_id: 2
            }
        }

        gin_vodka_recipe_info = {
            'name': 'Gin and Vodka',
            'instructions': [
                'Add 1 part Gin',
                'Add 1 part Vodka',
                'Enjoy!'
            ],
            'ingredients': {
                self.vodka_id: 1,
                self.gin_id: 1
            }
        }

        pina_colada_recipe_info = {
            'name': 'Pina Colada',
            'instructions': [
                'Add 3 parts pineapple juice',
                'Add 1 part white rum',
                'Add 1 part coconut cream',
                'Mixed with crushed ice until smooth',
                'Pour into chilled glass'
            ],
            'ingredients': {
                self.pineapple_juice_id: 3,
                self.white_rum_id: 1,
                self.coconut_cream_id: 1
            }
        }

        profile.create_recipe(pina_colada_recipe_info)
        profile.create_recipe(gin_vodka_recipe_info)
        profile.create_recipe(screwdriver_recipe_info)
        self.screwdriver = Recipe.objects.get(name='Screwdriver')
        self.gin_vodka = Recipe.objects.get(name='Gin and Vodka')
        self.pina_colada = Recipe.objects.get(name='Pina Colada')

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




