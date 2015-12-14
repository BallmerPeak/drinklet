from django.test import TestCase
from django.contrib.auth.models import User
from ingredients.models import Ingredient
from recipes.models import Recipe, RecipeIngredients
from user.models import UserProfile, UserIngredients
from recipes.views import make_drink
from django.test import RequestFactory


class MakeDrinkTestCase(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user('testuser', 'email@email.com', 'password')
        self.profile = UserProfile.objects.create(user=self.user)
        self.ingredients = Ingredient.objects.bulk_create([Ingredient(name='vodka', category='alcohol'),
                                                          Ingredient(name='rum', category='alcohol'),
                                                          Ingredient(name='gin', category='alcohol'),
                                                          Ingredient(name='orange juice', category='juice'),
                                                          Ingredient(name='pineapple juice', category='juice')])

        self.vodka = Ingredient.objects.get(name='vodka')
        self.rum = Ingredient.objects.get(name='rum')
        self.gin = Ingredient.objects.get(name='gin')
        self.oj = Ingredient.objects.get(name='orange juice')
        self.pineapple = Ingredient.objects.get(name='pineapple juice')

        def create_drink(name, ratings_sum, num_ratings, author):
            recipe = Recipe.objects.create(name=name,
                                           ratings_sum=ratings_sum,
                                           num_ratings=num_ratings,
                                           author=author)
            setattr(self, name.replace(" ", "_"), recipe)

        def add_ingredients_to_drink(recipe, ingredients):
            drink_ingredients = []
            for ingredient, quantity in ingredients:
                drink_ingredients.append(RecipeIngredients(recipe=recipe,
                                                           ingredient=ingredient,
                                                           quantity=quantity))

            RecipeIngredients.objects.bulk_create(drink_ingredients)

        def create_pantry():
            self.user_ingredients = UserIngredients.objects.bulk_create([
                UserIngredients(user=self.profile, ingredient=self.gin, quantity=10.0),
                UserIngredients(user=self.profile, ingredient=self.vodka, quantity=10.0),
                UserIngredients(user=self.profile, ingredient=self.pineapple, quantity=2.0)])

        create_drink('screwdriver', 120, 40, self.profile)
        create_drink('gin and vodka', 10, 40, self.profile)
        create_drink('gross drink', 10, 40, self.profile)

        add_ingredients_to_drink(self.screwdriver, [(self.vodka, 1),
                                                    (self.oj, 2)])

        add_ingredients_to_drink(self.gin_and_vodka, [(self.vodka, 2),
                                                      (self.gin, 2)])

        add_ingredients_to_drink(self.gross_drink, [(self.vodka, 2),
                                                    (self.pineapple, 4)])

        create_pantry()

    def test_success(self):
        request = self.factory.post('recipes/makedrink', {'recipe': Recipe.objects.get(name='gin and vodka').id})
        request.user = self.user
        self.assertEqual(make_drink(request).status_code, 200)

    def test_user_doesnt_have_ingredient(self):
        request = self.factory.post('recipes/makedrink', {'recipe': Recipe.objects.get(name='screwdriver').id})
        request.user = self.user
        self.assertEqual(make_drink(request).content, b'error')

    def test_user_doesnt_have_quantity(self):
        request = self.factory.post('recipes/makedrink', {'recipe': Recipe.objects.get(name='gross drink').id})
        request.user = self.user
        self.assertEqual(make_drink(request).content, b'error')
