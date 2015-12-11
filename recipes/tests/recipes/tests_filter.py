import json

from django.test import TransactionTestCase, Client
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from recipes.models import Recipe
from user.models import UserProfile
from ingredients.models import Ingredient


class RecipeFilterTest(TransactionTestCase):

    def setUp(self):
        self.c = Client()
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
        profile.set_rating(self.screwdriver.id,4)
        profile.set_rating(self.gin_vodka.id,5)
        profile.set_rating(self.pina_colada.id,3)

        # Filter specific values
        self.ingredients = []
        self.query = ''
        self.limit = 6
        self.order_by = 'name'
        self.order = 'asc'

    def test_no_values_get(self):
        response = self.c.get(reverse('recipes.search'))
        context = list(response.context[-1])[1]
        self.assertEqual(context['query'], self.query)
        self.assertEqual(context['search_ingredients'], self.ingredients)
        self.assertEqual(context['limit'], self.limit)
        self.assertEqual(context['order'], self.order)
        self.assertEqual(context['order_by'], self.order_by)
        self.assertEqual(len(context['results'].object_list), 3)

    def test_no_values_post(self):
        data = json.dumps({})
        response = self.c.post(reverse('recipes.search'), {'data': data}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        context = list(response.context[-1])[1]
        self.assertEqual(context['query'], self.query)
        self.assertEqual(context['search_ingredients'], self.ingredients)
        self.assertEqual(context['limit'], self.limit)
        self.assertEqual(context['order'], self.order)
        self.assertEqual(context['order_by'], self.order_by)
        self.assertEqual(len(context['results'].object_list), 3)

    def test_ingredients_is_bad_str(self):
        data = json.dumps({'search_ingredients': 'bad string'})
        response = self.c.post(reverse('recipes.search'), {'data': data}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        context = list(response.context[-1])[1]
        self.assertEqual(context['search_ingredients'], self.ingredients)
        self.assertEqual(len(context['results'].object_list), 3)

    def test_ingredients_is_matching(self):
        data = json.dumps({
            'search_ingredients': '{},{},{}'.format(self.pineapple_juice_id, self.white_rum_id, self.coconut_cream_id)
        })
        response = self.c.post(reverse('recipes.search'), {'data': data}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        context = list(response.context[-1])[1]
        self.assertListEqual([self.pineapple_juice_id, self.white_rum_id, self.coconut_cream_id],
                             context['search_ingredients'])
        self.assertEqual(len(context['results'].object_list), 1)

    def test_ingredients_is_not_matching(self):
        data = json.dumps({'search_ingredients': '{},{}'.format(self.gin_id, self.white_rum_id)})
        response = self.c.post(reverse('recipes.search'), {'data': data}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        try:
            context = list(response.context[-1])[1]
        except KeyError:
            context = response.context.dicts[-1]

        self.assertEqual(context['search_ingredients'], [self.gin_id, self.white_rum_id])
        self.assertEqual(len(context['results'].object_list), 0)

    def test_query_is_matching_recipe_name(self):
        data = json.dumps({'query': 'gin'})
        response = self.c.post(reverse('recipes.search'), {'data': data}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        context = list(response.context[-1])[1]
        self.assertEqual(context['query'], 'gin')
        self.assertEqual(len(context['results'].object_list), 1)
        self.assertEqual(context['results'].object_list[0], self.gin_vodka)

    def test_query_is_matching_author_name(self):
        data = json.dumps({'query': 'testuser'})
        response = self.c.post(reverse('recipes.search'), {'data': data}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        context = list(response.context[-1])[1]
        self.assertEqual(context['query'], 'testuser')
        self.assertEqual(len(context['results'].object_list), 3)
        for recipe in context['results'].object_list:
            self.assertEqual(recipe.author.user.username, 'testuser')

    def test_query_is_matching_an_ingredient(self):
        data = json.dumps({'query': 'gin'})
        response = self.c.post(reverse('recipes.search'), {'data': data}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        context = list(response.context[-1])[1]
        self.assertEqual(context['query'], 'gin')
        self.assertEqual(len(context['results'].object_list), 1)
        self.assertEqual(context['results'].object_list[0], self.gin_vodka)
        has_ingredient = False
        for recipe_ingredient in context['results'].object_list[0].recipeingredients_set.all():
            if 'gin' in recipe_ingredient.ingredient.name:
                has_ingredient = True
                break
        self.assertTrue(has_ingredient)

    def test_query_is_not_matching(self):
        data = json.dumps({'query': 'abc'})
        response = self.c.post(reverse('recipes.search'), {'data': data}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        try:
            context = list(response.context[-1])[1]
        except KeyError:
            context = response.context.dicts[-1]

        self.assertEqual(context['query'], 'abc')
        self.assertEqual(len(context['results'].object_list), 0)

    def test_order_by_name_asc(self):
        data = json.dumps({'order_by': 'name', 'order': 'asc'})
        response = self.c.post(reverse('recipes.search'), {'data': data}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        context = list(response.context[-1])[1]
        self.assertEqual(context['order_by'], 'name')
        self.assertEqual(context['order'], 'asc')
        self.assertEqual(len(context['results'].object_list), 3)
        self.assertEqual(context['results'].object_list[0], self.gin_vodka)
        self.assertEqual(context['results'].object_list[1], self.pina_colada)
        self.assertEqual(context['results'].object_list[2], self.screwdriver)

    def test_order_by_name_desc(self):
        data = json.dumps({'order_by': 'name', 'order': 'desc'})
        response = self.c.post(reverse('recipes.search'), {'data': data}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        context = list(response.context[-1])[1]
        self.assertEqual(context['order_by'], 'name')
        self.assertEqual(context['order'], 'desc')
        self.assertEqual(len(context['results'].object_list), 3)
        self.assertEqual(context['results'].object_list[0], self.screwdriver)
        self.assertEqual(context['results'].object_list[1], self.pina_colada)
        self.assertEqual(context['results'].object_list[2], self.gin_vodka)

    def test_order_by_ratings_asc(self):
        data = json.dumps({'order_by': 'ratings', 'order': 'asc'})
        response = self.c.post(reverse('recipes.search'), {'data': data}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        context = list(response.context[-1])[1]
        self.assertEqual(context['order_by'], 'ratings')
        self.assertEqual(context['order'], 'asc')
        self.assertEqual(len(context['results'].object_list), 3)
        self.assertEqual(context['results'].object_list[0], self.pina_colada)
        self.assertEqual(context['results'].object_list[1], self.screwdriver)
        self.assertEqual(context['results'].object_list[2], self.gin_vodka)

    def test_order_by_ratings_desc(self):
        data = json.dumps({'order_by': 'ratings', 'order': 'desc'})
        response = self.c.post(reverse('recipes.search'), {'data': data}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        context = list(response.context[-1])[1]
        self.assertEqual(context['order_by'], 'ratings')
        self.assertEqual(context['order'], 'desc')
        self.assertEqual(len(context['results'].object_list), 3)
        self.assertEqual(context['results'].object_list[0], self.gin_vodka)
        self.assertEqual(context['results'].object_list[1], self.screwdriver)
        self.assertEqual(context['results'].object_list[2], self.pina_colada)
