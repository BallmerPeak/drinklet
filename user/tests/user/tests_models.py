from django.db import transaction
from django.test import TestCase
from django.contrib.auth.models import User
from ingredients.models import Ingredient
from recipes.models import Recipe, RecipeIngredients
from django.db.utils import IntegrityError
from user.models import UserProfile, UserIngredients

# Create your tests here.


class UserProfileTestCase(TestCase):
    # noinspection PyUnresolvedReferences
    def setUp(self):
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

        add_ingredients_to_drink(self.screwdriver, [(self.vodka, 1),
                                                    (self.oj, 2)])

        add_ingredients_to_drink(self.gin_and_vodka, [(self.vodka, 2),
                                                      (self.gin, 2)])

        create_pantry()

    def test_create_or_get_profile(self):
        profile = UserProfile.get_or_create_profile(self.user)
        self.assertEqual(self.profile, profile)
        self.assertEqual('testuser', profile.user.username)
        self.assertEqual('email@email.com', profile.user.email)
        self.assertNotEqual('password', profile.user.password)

    def test_set_favorites(self):
        # Test set 1 favorite
        # noinspection PyUnresolvedReferences
        def set_one_favorite():
            favorites = self.profile.set_favorites(self.screwdriver.id)
            self.assertIn(self.screwdriver, favorites)

        # Test set duplicate favorite
        # noinspection PyUnresolvedReferences
        def set_duplicate_favorite():
            expected_favorites = self.profile.favorites.all()
            favorites = self.profile.set_favorites(self.screwdriver.id)
            self.assertEqual(1, favorites.count())
            self.assertCountEqual(expected_favorites, favorites)
            self.assertListEqual(list(expected_favorites), list(favorites))

        # Test set 2nd favorite
        # noinspection PyUnresolvedReferences
        def set_second_favorite():
            favorites = self.profile.set_favorites(self.gin_and_vodka.id)
            self.assertEqual(2, favorites.count())
            self.assertListEqual([self.screwdriver, self.gin_and_vodka], list(favorites))

        # Test removing gin and vodka as favorite
        # noinspection PyUnresolvedReferences
        def remove_one_favorite():
            favorites = self.profile.set_favorites(self.gin_and_vodka.id, True)
            self.assertEqual(1, favorites.count())
            self.assertListEqual([self.screwdriver], list(favorites))

        set_one_favorite()
        set_duplicate_favorite()
        set_second_favorite()
        remove_one_favorite()

    def test_get_favorites(self):
        # Test get favorite with 1 favorite
        # noinspection PyUnresolvedReferences
        def get_one_favorite():
            self.assertListEqual([], list(self.profile.get_favorites()))
            self.profile.favorites.add(self.screwdriver)
            self.assertListEqual([self.screwdriver], list(self.profile.get_favorites()))

        # Test get favorite with 2 favorites
        # noinspection PyUnresolvedReferences
        def get_two_favorites():
            self.profile.favorites.add(self.gin_and_vodka)
            self.assertListEqual([self.screwdriver, self.gin_and_vodka], list(self.profile.get_favorites()))

        def get_user_stats():
            recipes = self.profile.get_favorites()
            self._check_recipe_stats(recipes)

        get_one_favorite()
        get_two_favorites()
        get_user_stats()

    # noinspection PyUnresolvedReferences
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
            self.gin_and_vodka = Recipe.objects.get(name='gin and vodka')
            self.assertEqual(11, self.gin_and_vodka.ratings_sum)
            self.assertEqual(41, self.gin_and_vodka.num_ratings)
            self.assertEqual(2, len(ratings))
            self.assertEqual(1, ratings[self.gin_and_vodka.id])

        set_initial_rating_first_drink()
        update_rating()
        set_initial_rating_second_drink()

    def test_add_user_ingredients(self):
        UserIngredients.objects.all().delete()
        rum_id = self.rum.id
        oj_id = self.oj.id
        pineapple_id = self.pineapple.id

        # Test adding ingredients into empty field
        def add_ingredients_first_time():
            ingredient_ids1 = [rum_id, oj_id, pineapple_id]
            ingredients = self.profile.add_user_ingredients(ingredient_ids1)
            self.assertListEqual(ingredient_ids1, list(self.profile.ingredients.values_list('id', flat=True)))
            self.assertEqual(3, len(ingredients))
            quantities = [ingredients[ing_id] for ing_id in ingredient_ids1]
            self.assertListEqual([0, 0, 0], quantities)
            return ingredients

        # Test adding duplicate ingredient
        def add_duplicate_ingredient():
            ingredient_ids2 = [rum_id, pineapple_id]
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
        UserIngredients.objects.all().delete()
        ingredient_ids = sorted([self.vodka.id, self.rum.id, self.gin.id, self.oj.id, self.pineapple.id])
        self.profile.add_user_ingredients(ingredient_ids)
        self.assertEqual(5, self.profile.ingredients.count())

        # Test deleting existing ingredient
        def delete_existing_ingredient():
            ingredients2 = self.profile.delete_user_ingredient(ingredient_ids[0])
            self.assertListEqual(ingredient_ids[1:], list(self.profile.ingredients.values_list('id', flat=True)))
            self.assertEqual(4, len(ingredients2))
            self.assertEqual(4, self.profile.ingredients.count())
            quantities = [ingredients2[ing_id] for ing_id in ingredient_ids[1:]]
            self.assertListEqual([0, 0, 0, 0], quantities)
            return ingredients2

        # Test deleting non-existent ingredient
        def delete_nonexistent_ingredient(ingredients2):
            fake_id = sum(ingredient_ids)
            ingredients3 = self.profile.delete_user_ingredient(fake_id)
            self.assertDictEqual(ingredients2, ingredients3)

        # Test deleting when field is empty
        def delete_from_empty_field():
            self.profile.delete_user_ingredient(ingredient_ids[1])
            self.profile.delete_user_ingredient(ingredient_ids[2])
            ingredients4 = self.profile.delete_user_ingredient(ingredient_ids[2])
            self.assertEqual(2, len(ingredients4))

        ingredient_dict = delete_existing_ingredient()
        delete_nonexistent_ingredient(ingredient_dict)
        delete_from_empty_field()

    def test_update_user_ingredient_quantity(self):
        vodka = UserIngredients.objects.get(ingredient=self.vodka)
        gin = UserIngredients.objects.get(ingredient=self.gin)
        pineapple_juice = UserIngredients.objects.get(ingredient=self.pineapple)

        self.assertEqual(3, self.profile.useringredients_set.count())
        self.assertEqual(self.profile, vodka.user)
        self.assertEqual(self.profile, gin.user)
        self.assertEqual(self.profile, pineapple_juice.user)
        self.assertEqual(10, vodka.quantity)
        self.assertEqual(10, gin.quantity)
        self.assertEqual(2, pineapple_juice.quantity)

        self.profile.update_user_ingredient_quantity(vodka.ingredient.id, 15)
        self.profile.update_user_ingredient_quantity(gin.ingredient.id, 5)
        self.profile.update_user_ingredient_quantity(pineapple_juice.ingredient.id, 1)

        vodka.refresh_from_db()
        gin.refresh_from_db()
        pineapple_juice.refresh_from_db()

        self.assertEqual(3, self.profile.useringredients_set.count())
        self.assertEqual(self.profile, vodka.user)
        self.assertEqual(self.profile, gin.user)
        self.assertEqual(self.profile, pineapple_juice.user)
        self.assertEqual(15, vodka.quantity)
        self.assertEqual(5, gin.quantity)
        self.assertEqual(1, pineapple_juice.quantity)

    def test_create_recipe(self):
        Recipe.objects.all().delete()
        self.assertEqual(0, Recipe.objects.count())

        vodka_id = self.vodka.id
        oj_id = self.oj.id
        gin_id = self.gin.id
        pineapple_juice_id = self.pineapple.id

        screwdriver_recipe = (
            'Screwdriver',
            [
                'Fill glass with ice',
                'Add 2 parts Orange Juice',
                'Add 1 part Vodka',
                'Shake well'
            ],
            {
                vodka_id: 1,
                oj_id: 2
            }
        )

        gin_vodka_recipe = (
            'Gin and Vodka',
            [
                'Add 1 part Gin',
                'Add 1 part Vodka',
                'Enjoy!'
            ],
            {
                vodka_id: 2,
                gin_id: 2
            }
        )

        fake_screwdriver_recipe = (
            'Screwdriver',
            [
                'This is fake',
                'Really fake'
            ],
            {
                vodka_id: 1,
                gin_id: 1
            }
        )

        # Recipe with new ingredients
        pina_colada_recipe = (
            'Pina Colada',
            [
                'Add 3 parts pineapple juice',
                'Add 1 part white rum',
                'Add 1 part coconut cream',
                'Mixed with crushed ice until smooth',
                'Pour into chilled glass'
            ],
            {
                pineapple_juice_id: 3,
                'white rum': ('alcohol', 1, 'oz'),
                'coconut cream': ('Miscellaneous', 1, 'oz')
            }
        )

        # Test creating 1 recipe
        def create_one_recipe():
            recipe1 = self.profile.create_recipe(*screwdriver_recipe)
            self.assertEqual(recipe1, self.profile.created_recipes.get(id=recipe1.id))
            self.assertEqual(1, self.profile.created_recipes.count())
            self.assertEqual(screwdriver_recipe[0].lower(), recipe1.name)
            self.assertEqual('~~~'.join(screwdriver_recipe[1]), recipe1.instructions_blob)
            self.assertEqual(screwdriver_recipe[2][vodka_id],
                             recipe1.recipeingredients_set.get(recipe=recipe1,
                                                               ingredient=vodka_id).quantity)
            self.assertEqual(screwdriver_recipe[2][oj_id],
                             recipe1.recipeingredients_set.get(recipe=recipe1,
                                                               ingredient=oj_id).quantity)
            return recipe1

        # Test Create 2nd recipe
        def create_second_recipe():
            recipe2 = self.profile.create_recipe(*gin_vodka_recipe)
            self.assertEqual(recipe2, self.profile.created_recipes.get(id=recipe2.id))
            self.assertEqual(2, self.profile.created_recipes.count())
            gin_vodka_obj = self.profile.created_recipes.get(name='gin and vodka')
            self.assertEqual(gin_vodka_recipe[0].lower(), gin_vodka_obj.name)
            self.assertEqual('~~~'.join(gin_vodka_recipe[1]), gin_vodka_obj.instructions_blob)
            self.assertEqual(gin_vodka_recipe[2][vodka_id],
                             gin_vodka_obj.recipeingredients_set.get(recipe=gin_vodka_obj,
                                                                     ingredient=vodka_id).quantity)
            self.assertEqual(gin_vodka_recipe[2][gin_id],
                             gin_vodka_obj.recipeingredients_set.get(recipe=gin_vodka_obj,
                                                                     ingredient=gin_id).quantity)

        # Test create duplicately named recipe
        def create_duplicately_named_recipe(recipe1):
            with self.assertRaises(IntegrityError):
                with transaction.atomic():
                    self.profile.create_recipe(*fake_screwdriver_recipe)

            self.assertEqual(2, self.profile.created_recipes.count())
            self.assertEqual(recipe1, self.profile.created_recipes.get(name='screwdriver'))

        # Test create recipe with new ingredients
        def create_with_new_ingredients():
            ingredient_count = Ingredient.objects.count()

            with self.assertRaises(Ingredient.DoesNotExist):
                with transaction.atomic():
                    Ingredient.objects.get(name='white rum')

            with self.assertRaises(Ingredient.DoesNotExist):
                with transaction.atomic():
                    Ingredient.objects.get(name='coconut cream')

            with self.assertRaises(Recipe.DoesNotExist):
                with transaction.atomic():
                    Recipe.objects.get(name='pina colada')

            recipe = self.profile.create_recipe(*pina_colada_recipe)
            pina_colada = Recipe.objects.get(name='pina colada')

            self.assertEqual(recipe, pina_colada)
            self.assertEqual(ingredient_count + 2, Ingredient.objects.count())

        new_recipe = create_one_recipe()
        create_second_recipe()
        create_duplicately_named_recipe(new_recipe)
        create_with_new_ingredients()

    def test_delete_recipe(self):
        Recipe.objects.all().delete()
        self.assertEqual(0, Recipe.objects.count())

        vodka_id = self.vodka.id
        oj_id = self.oj.id

        screwdriver_recipe = (
            'Screwdriver',
            [
                'Fill glass with ice',
                'Add 2 parts Orange Juice',
                'Add 1 part Vodka',
                'Shake well'
            ],
            {
                vodka_id: 1,
                oj_id: 2
            }
        )

        screwdriver = self.profile.create_recipe(*screwdriver_recipe)
        screwdriver1 = self.profile.created_recipes.get(id=screwdriver.id)
        screwdriver2 = Recipe.objects.get(id=screwdriver.id)

        self.assertEqual(screwdriver, screwdriver1)
        self.assertEqual(screwdriver, screwdriver2)

        profile = self.profile.delete_recipe(screwdriver.id)

        with self.assertRaises(Recipe.DoesNotExist):
            with transaction.atomic():
                profile.created_recipes.get(id=screwdriver.id)

        with self.assertRaises(Recipe.DoesNotExist):
            with transaction.atomic():
                Recipe.objects.get(id=screwdriver.id)

        recipes = Recipe.objects.all()
        self.assertEqual(0, recipes.count())

    def test_get_created_recipes(self):
        Recipe.objects.all().delete()
        self.assertEqual(0, Recipe.objects.count())

        vodka_id = self.vodka.id
        oj_id = self.oj.id
        gin_id = self.gin.id

        screwdriver_recipe = (
            'Screwdriver',
            [
                'Fill glass with ice',
                'Add 2 parts Orange Juice',
                'Add 1 part Vodka',
                'Shake well'
            ],
            {
                vodka_id: 1,
                oj_id: 2
            }
        )

        gin_vodka_recipe = (
            'Gin and Vodka',
            [
                'Add 1 part Gin',
                'Add 1 part Vodka',
                'Enjoy!'
            ],
            {
                vodka_id: 2,
                gin_id: 2
            }
        )

        pina_colada_recipe = (
            'Pineapple Vodka',
            [
                'Add 3 parts pineapple juice',
                'Add 1 part vodka',
                'Mixed with crushed ice until smooth',
                'Pour into chilled glass'
            ],
            {
                self.pineapple.id: 3,
                self.vodka.id: 1
            }
        )

        self.profile.create_recipe(*screwdriver_recipe)
        self.profile.create_recipe(*gin_vodka_recipe)
        self.profile.create_recipe(*pina_colada_recipe)

        recipes = self.profile.get_created_recipes()

        self.assertEqual(3, recipes.count())

        self._check_recipe_stats(recipes)

    def test_get_all_recipes(self):
        recipes = self.profile.get_all_recipes()
        self.assertEqual(2, recipes.count())

        self._check_recipe_stats(recipes)

    # noinspection PyUnresolvedReferences
    def test_get_recipes_by_ingredients(self):
        recipes = self.profile.get_recipes_by_ingredients([
            self.vodka.id, self.oj.id, self.gin.id
        ])

        recipes.sort(key=lambda recipe: recipe.id)
        expected_recipes = sorted([self.gin_and_vodka, self.screwdriver], key=lambda recipe: recipe.id)

        self.assertEqual(2, len(recipes))
        self.assertListEqual(expected_recipes, recipes)

        self._check_recipe_stats(recipes)

    def _check_recipe_stats(self, recipes):
        for recipe in recipes:
            if recipe.name == 'screwdriver':
                self.assertEqual(0, recipe.num_can_make)
                self.assertEqual(1, len(recipe.missing_ingredients))
                missing_ingredient, qty_missing = recipe.missing_ingredients[0]
                self.assertEqual(self.oj.id, missing_ingredient)
                self.assertEqual(2, qty_missing)

            if recipe.name == 'gin and vodka':
                self.assertEqual(5, recipe.num_can_make)
                self.assertEqual(0, len(recipe.missing_ingredients))

            if recipe.name == 'pineapple vodka':
                self.assertEqual(0, recipe.num_can_make)
                self.assertEqual(1, len(recipe.missing_ingredients))
                missing_ingredient, qty_missing = recipe.missing_ingredients[0]
                self.assertEqual(self.pineapple.id, missing_ingredient)
                self.assertEqual(1, qty_missing)