from django.test import TestCase
from ingredients.models import Ingredient
# Create your tests here.


class IngredientTestCase(TestCase):
    def setUp(self):
        Ingredient.objects.bulk_create([Ingredient(name='Vodka', category='alcohol'),
                                        Ingredient(name='Rum', category='alcohol'),
                                        Ingredient(name='Gin', category='alcohol'),
                                        Ingredient(name='Orange Juice', category='juice'),
                                        Ingredient(name='Pineapple Juice', category='juice')])
        self.ingredients = list(Ingredient.objects.all())

    def test_get_all_ingredients(self):
        ingredients = [ingredient for sub_list in list(Ingredient.get_all_ingredients().values())
                       for ingredient in sub_list]
        ingredients.sort(key=lambda ingredient: ingredient.id)
        self.assertEqual(len(self.ingredients), len(ingredients))
        self.assertListEqual(self.ingredients, ingredients)
