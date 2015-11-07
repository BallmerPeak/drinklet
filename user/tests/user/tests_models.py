from django.db import transaction
from django.test import TestCase
from django.contrib.auth.models import User
from ingredients.models import Ingredient
from recipes.models import Recipe, RecipeIngredients
from django.db.utils import IntegrityError
from user.models import UserProfile

# Create your tests here.


class UserProfileTestCase(TestCase):
<<<<<<< HEAD
    # noinspection PyUnresolvedReferences
=======
>>>>>>> dev
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'email@email.com', 'password')
        self.profile = UserProfile.objects.create(user=self.user)
        self.ingredients = Ingredient.objects.bulk_create([Ingredient(name='Vodka', category='alcohol'),
                                                          Ingredient(name='Rum', category='alcohol'),
                                                          Ingredient(name='Gin', category='alcohol'),
                                                          Ingredient(name='Orange Juice', category='juice'),
                                                          Ingredient(name='Pineapple Juice', category='juice')])

        def create_drink(name, ratings_sum, num_ratings):
            recipe = Recipe.objects.create(name=name,
                                           ratings_sum=ratings_sum,
                                           num_ratings=num_ratings)
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
<<<<<<< HEAD
        profile = UserProfile.get_or_create_profile(self.user)
=======
        profile = UserProfile.create_or_get_profile(self.user)
>>>>>>> dev
        self.assertEqual(self.profile, profile)
        self.assertEqual('testuser', profile.user.username)
        self.assertEqual('email@email.com', profile.user.email)
        self.assertNotEqual('password', profile.user.password)

    def test_set_favorites(self):
        # Test set 1 favorite
<<<<<<< HEAD
        # noinspection PyUnresolvedReferences
=======
>>>>>>> dev
        def set_one_favorite():
            favorites = self.profile.set_favorites(self.screwdriver.id)
            self.assertIn(self.screwdriver, favorites)

        # Test set duplicate favorite
<<<<<<< HEAD
        # noinspection PyUnresolvedReferences
=======
>>>>>>> dev
        def set_duplicate_favorite():
            expected_favorites = self.profile.favorites.all()
            favorites = self.profile.set_favorites(self.screwdriver.id)
            self.assertEqual(1, favorites.count())
            self.assertCountEqual(expected_favorites, favorites)
            self.assertListEqual(list(expected_favorites), list(favorites))

        # Test set 2nd favorite
<<<<<<< HEAD
        # noinspection PyUnresolvedReferences
=======
>>>>>>> dev
        def set_second_favorite():
            favorites = self.profile.set_favorites(self.gin_and_vodka.id)
            self.assertEqual(2, favorites.count())
            self.assertListEqual([self.screwdriver, self.gin_and_vodka], list(favorites))

        set_one_favorite()
        set_duplicate_favorite()
        set_second_favorite()

    def test_get_favorites(self):
        # Test get favorite with 1 favorite
<<<<<<< HEAD
        # noinspection PyUnresolvedReferences
=======
>>>>>>> dev
        def get_one_favorite():
            self.assertListEqual([], list(self.profile.get_favorites()))
            self.profile.favorites.add(self.screwdriver)
            self.assertListEqual([self.screwdriver], list(self.profile.get_favorites()))

        # Test get favorite with 2 favorites
<<<<<<< HEAD
        # noinspection PyUnresolvedReferences
=======
>>>>>>> dev
        def get_two_favorites():
            self.profile.favorites.add(self.gin_and_vodka)
            self.assertListEqual([self.screwdriver, self.gin_and_vodka], list(self.profile.get_favorites()))

        get_one_favorite()
        get_two_favorites()

<<<<<<< HEAD
    # noinspection PyUnresolvedReferences
=======
>>>>>>> dev
    def test_set_rating(self):
        self.assertEqual(120, self.screwdriver.ratings_sum)
        self.assertEqual(40, self.screwdriver.num_ratings)

        # Test setting initial rating
        def set_initial_rating_first_drink():
            ratings = self.profile.set_rating(self.screwdriver.id, 4)
            self.screwdriver = Recipe.objects.get(name='screwdriver')
            self.assertEqual(124, self.screwdriver.ratings_sum)
            self.assertEqual(41, self.screwdriver.num_ratings)
            self.assertEqual(1, len(ratings))
            self.assertEqual(4, ratings[self.screwdriver.id])

        # Test update an already set rating
        def update_rating():
            ratings = self.profile.set_rating(self.screwdriver.id, 2)
            self.screwdriver = Recipe.objects.get(name='screwdriver')
            self.assertEqual(122, self.screwdriver.ratings_sum)
            self.assertEqual(41, self.screwdriver.num_ratings)
            self.assertEqual(1, len(ratings))
            self.assertEqual(2, ratings[self.screwdriver.id])

        # Test setting a second rating
        def set_initial_rating_second_drink():
            ratings = self.profile.set_rating(self.gin_and_vodka.id, 1)
            self.gin_and_vodka = Recipe.objects.get(name='gin_and_vodka')
            self.assertEqual(11, self.gin_and_vodka.ratings_sum)
            self.assertEqual(41, self.gin_and_vodka.num_ratings)
            self.assertEqual(2, len(ratings))
            self.assertEqual(1, ratings[self.gin_and_vodka.id])

        set_initial_rating_first_drink()
        update_rating()
        set_initial_rating_second_drink()

    def test_add_user_ingredients(self):
        ingredient_ids = Ingredient.objects.values_list('id', flat=True)

        # Test adding ingredients into empty field
        def add_ingredients_first_time():
            ingredient_ids1 = list(ingredient_ids[:3])
            ingredients = self.profile.add_user_ingredients(ingredient_ids1)
            self.assertListEqual(ingredient_ids1, list(self.profile.ingredients.values_list('id', flat=True)))
            self.assertEqual(3, len(ingredients))
            quantities = [ingredients[ing_id] for ing_id in ingredient_ids1]
            self.assertListEqual([0, 0, 0], quantities)
            return ingredients

        # Test adding duplicate ingredient
        def add_duplicate_ingredient():
            ingredient_ids2 = ingredient_ids[2:4]
            with self.assertRaises(IntegrityError):
                with transaction.atomic():
                    self.profile.add_user_ingredients(ingredient_ids2)

        # Test adding empty list
        def add_empty_list_of_ingredients(ingredients):
            ingredients1 = self.profile.add_user_ingredients([])
            self.assertDictEqual(ingredients, ingredients1)

        ingredient_dict = add_ingredients_first_time()
        add_duplicate_ingredient()
        add_empty_list_of_ingredients(ingredient_dict)

    def test_delete_user_ingredient(self):
        # Set up
        ingredient_ids = Ingredient.objects.values_list('id', flat=True)
        ingredient_ids1 = list(ingredient_ids[:3])
        self.profile.add_user_ingredients(ingredient_ids1)
        self.assertEqual(3, self.profile.ingredients.count())

        # Test deleting existing ingredient
        def delete_existing_ingredient():
            ingredients2 = self.profile.delete_user_ingredient(ingredient_ids1[0])
            self.assertListEqual(ingredient_ids1[1:], list(self.profile.ingredients.values_list('id', flat=True)))
            self.assertEqual(2, len(ingredients2))
            self.assertEqual(2, self.profile.ingredients.count())
            quantities = [ingredients2[ing_id] for ing_id in ingredient_ids1[1:]]
            self.assertListEqual([0, 0], quantities)
            return ingredients2

        # Test deleting non-existent ingredient
        def delete_nonexistent_ingredient(ingredients2):
            fake_id = sum(ingredient_ids1)
            ingredients3 = self.profile.delete_user_ingredient(fake_id)
            self.assertDictEqual(ingredients2, ingredients3)

        # Test deleting when field is empty
        def delete_from_empty_field():
            self.profile.delete_user_ingredient(ingredient_ids1[1])
            self.profile.delete_user_ingredient(ingredient_ids1[2])
            ingredients4 = self.profile.delete_user_ingredient(ingredient_ids1[2])
            self.assertEqual(0, len(ingredients4))

        ingredient_dict = delete_existing_ingredient()
        delete_nonexistent_ingredient(ingredient_dict)
        delete_from_empty_field()

    def test_create_recipe(self):
        vodka_id = Ingredient.objects.get(name='Vodka').id
        oj_id = Ingredient.objects.get(name='Orange Juice').id
        gin_id = Ingredient.objects.get(name='Gin').id

        screwdriver_recipe = {
            'name': 'Screwdriver',
            'instructions': [
                'Fill glass with ice',
                'Add 2 parts Orange Juice',
                'Add 1 part Vodka',
                'Shake well'
            ],
            'ingredients': {
                vodka_id: 1,
                oj_id: 2
            }
        }

        gin_vodka_recipe = {
            'name': 'Gin and Vodka',
            'instructions': [
                'Add 1 part Gin',
                'Add 1 part Vodka',
                'Enjoy!'
            ],
            'ingredients': {
                vodka_id: 1,
                gin_id: 1
            }
        }

        fake_screwdriver_recipe = {
            'name': 'Screwdriver',
            'instructions': [
                'This is fake',
                'Really fake'
            ],
            'ingredients': {
                vodka_id: 1,
                gin_id: 1
            }
        }

        # Test creating 1 recipe
        def create_one_recipe():
            recipes1 = self.profile.create_recipe(screwdriver_recipe)
            self.assertListEqual(list(recipes1), list(self.profile.created_recipes.all()))
            self.assertEqual(1, len(recipes1))
            self.assertEqual(screwdriver_recipe['name'], recipes1[0].name)
            self.assertEqual('~~~'.join(screwdriver_recipe['instructions']), recipes1[0].instructions_blob)
            self.assertEqual(screwdriver_recipe['ingredients'][vodka_id],
                             recipes1[0].recipeingredients_set.get(recipe=recipes1[0],
                                                                   ingredient=vodka_id).quantity)
            self.assertEqual(screwdriver_recipe['ingredients'][oj_id],
                             recipes1[0].recipeingredients_set.get(recipe=recipes1[0],
                                                                   ingredient=oj_id).quantity)
            return recipes1

        # Test Create 2nd recipe
        def create_second_recipe():
            recipes2 = self.profile.create_recipe(gin_vodka_recipe)
            self.assertListEqual(list(recipes2), list(self.profile.created_recipes.all()))
            self.assertEqual(2, len(recipes2))
            gin_vodka_obj = recipes2.get(name='Gin and Vodka')
            self.assertEqual(gin_vodka_recipe['name'], gin_vodka_obj.name)
            self.assertEqual('~~~'.join(gin_vodka_recipe['instructions']), gin_vodka_obj.instructions_blob)
            self.assertEqual(gin_vodka_recipe['ingredients'][vodka_id],
                             gin_vodka_obj.recipeingredients_set.get(recipe=gin_vodka_obj,
                                                                     ingredient=vodka_id).quantity)
            self.assertEqual(gin_vodka_recipe['ingredients'][gin_id],
                             gin_vodka_obj.recipeingredients_set.get(recipe=gin_vodka_obj,
                                                                     ingredient=gin_id).quantity)

        # Test create duplicately named recipe
        def create_duplicately_named_recipe(recipes1):
            with self.assertRaises(IntegrityError):
                with transaction.atomic():
                    self.profile.create_recipe(fake_screwdriver_recipe)

            self.assertEqual(2, self.profile.created_recipes.count())
            self.assertEqual(recipes1[0], self.profile.created_recipes.get(name='Screwdriver'))

        recipes = create_one_recipe()
        create_second_recipe()
        create_duplicately_named_recipe(recipes)
<<<<<<< HEAD

    def test_delete_recipe(self):
        Recipe.objects.all().delete()
        vodka_id = Ingredient.objects.get(name='Vodka').id
        oj_id = Ingredient.objects.get(name='Orange Juice').id

        screwdriver_recipe = {
            'name': 'Screwdriver',
            'instructions': [
                'Fill glass with ice',
                'Add 2 parts Orange Juice',
                'Add 1 part Vodka',
                'Shake well'
            ],
            'ingredients': {
                vodka_id: 1,
                oj_id: 2
            }
        }

        recipes = self.profile.create_recipe(screwdriver_recipe)
        screwdriver = recipes.get(name='Screwdriver')

        profile = self.profile.delete_recipe(screwdriver.id)

        with self.assertRaises(Recipe.DoesNotExist):
            with transaction.atomic():
                profile.created_recipes.get(id=screwdriver.id)

        with self.assertRaises(Recipe.DoesNotExist):
            with transaction.atomic():
                Recipe.objects.get(id=screwdriver.id)

        recipes = Recipe.objects.all()
        self.assertEqual(0, recipes.count())
=======
>>>>>>> dev
