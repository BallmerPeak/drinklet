from django.test import TestCase
from django.contrib.auth.models import User
from ingredients.models import Ingredient
from recipes.models import Recipe, RecipeIngredients
from django.db.utils import IntegrityError
from user.models import UserProfile

# Create your tests here.


# noinspection PyUnresolvedReferences
class UserProfileTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'email@email.com', 'password')
        self.profile = UserProfile.objects.create(user=self.user)
        self.ingredients = Ingredient.objects.bulk_create([Ingredient(name='Vodka', category='alcohol'),
                                                          Ingredient(name='Rum', category='alcohol'),
                                                          Ingredient(name='Gin', category='alcohol'),
                                                          Ingredient(name='Orange Juice', category='juice'),
                                                          Ingredient(name='Pineapple Juice', category='juice')])

        def create_drink(name, ratings_sum, total_ratings):
            recipe = Recipe.objects.create(name=name,
                                           ratings_sum=ratings_sum,
                                           total_ratings=total_ratings)
            setattr(self, name, recipe)

        def add_ingredients_to_drink(recipe, ingredients):
            drink_ingredients = []
            for ingredient, quantity in ingredients:
                drink_ingredients.append(RecipeIngredients(recipe=recipe,
                                                           ingredient=ingredient,
                                                           quantity=quantity))

            RecipeIngredients.objects.bulk_create(drink_ingredients)

        create_drink('screwdriver', 120, 40)
        create_drink('gin_and_vodka', 10, 40)

        add_ingredients_to_drink(self.screwdriver, [(Ingredient.objects.get(name='Vodka'), 1),
                                                    (Ingredient.objects.get(name='Orange Juice'), 2)])

        add_ingredients_to_drink(self.gin_and_vodka, [(Ingredient.objects.get(name='Vodka'), 2),
                                                      (Ingredient.objects.get(name='Gin'), 2)])

    def test_create_or_get_profile(self):
        profile = UserProfile.create_or_get_profile(self.user)
        self.assertEqual(self.profile, profile)
        self.assertEqual('testuser', profile.user.username)
        self.assertEqual('email@email.com', profile.user.email)
        self.assertNotEqual('password', profile.user.password)

    def test_set_favorites(self):
        favorites = self.profile.set_favorites(self.screwdriver.id)

        self.assertIn(self.screwdriver, favorites)

        favorites2 = self.profile.set_favorites(self.screwdriver.id)

        self.assertEqual(1, favorites2.count())
        self.assertCountEqual(favorites, favorites2)
        self.assertListEqual(list(favorites), list(favorites2))
        self.assertEqual(favorites[0], favorites2[0])
