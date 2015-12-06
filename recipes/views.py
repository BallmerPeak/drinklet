from collections import OrderedDict

from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.views.generic import View
from django.core.context_processors import csrf
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.utils.http import urlencode
import json
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages

from .forms.recipes.recipe_form import RecipeForm, CATEGORY_NAME, INGREDIENT_NAME, INSTRUCTION_NAME, QTY_NAME, UOM_NAME
from .models import Recipe, Ingredient
from user.models import UserProfile


def _filter_recipes(ingredients, query, limit, order_by, order, page, user=None):
    """
    Build Paginator of results from filtering Recipes
    """
    # Get Recipe calling object
    call_object = Recipe if user is None else user
    # Make sure the list contains ids as integers
    if ingredients is None:
        ingredients = []
    else:
        if isinstance(ingredients, str):
            ingredients = ingredients.split(',')
        try:
            ingredients = list(map(int, ingredients))
        except ValueError:
            ingredients = []

    # If the query is not set, default it to empty
    if query is None:
        query = ""

    # If the limit is not set, default it to 10
    if limit is None:
        limit = 6

    # If the order_by is not set, default it to name
    if order_by is None:
        order_by = 'name'

    # If the order is not set, default it to asc
    if order is None:
        order = 'asc'

    # If the page is not set, default it to 1
    if page is None:
        page = 1

    # Get list of recipes based on ingredients
    if len(ingredients):
        recipes = call_object.get_recipes_by_ingredients(ingredients)
    # Get all recipes
    else:
        recipes = call_object.get_all_recipes()

    # Sort results by name
    if order_by == 'name':
        recipes = sorted(recipes, key=lambda r: r.name)
    # Sort results by ratings
    elif order_by == 'ratings':
        recipes = sorted(recipes, key=lambda r: r.ratings_sum / float(r.num_ratings) if r.num_ratings > 0 else r.num_ratings)

    # Order results in descending order
    if order == 'desc':
        recipes = [recipe for recipe in reversed(recipes) if query in recipe.name]
    # Order results in ascending order
    else:
        recipes = [recipe for recipe in recipes if query in recipe.name]

    paginator = Paginator(recipes, limit)

    # Grab the Recipe objects corresponding to passed in page
    try:
        results = paginator.page(page)
    # Invalid page passed in, give page 1
    except PageNotAnInteger:
        results = paginator.page(1)
    # Invalid page passed in, give page 1
    except EmptyPage:
        results = paginator.page(1)

    # Return all of the values
    return {
        'query': query,
        'limit': limit,
        'order_by': order_by,
        'order': order,
        'ingredients': ingredients,
        'results': results
    }


class SearchRecipes(View):
    def get(self, request):
        """
        Lists all recipes
        :param request:
        """
        # Create new Paginator object for Recipe objects
        profile = None
        if request.user.is_authenticated():
            profile = UserProfile.get_or_create_profile(request.user)

        filter_res = _filter_recipes(
            [],
            "",
            request.GET.get('limit'),
            request.GET.get('order_by'),
            request.GET.get('order'),
            request.GET.get('page'),
            profile,
        )
            
        favorites = None
        user_recipes = None
        if profile:
            favorites = profile.get_favorites()
            user_recipes = profile.get_all_recipes()

        context = {
            'query': "",
            'limit': filter_res['limit'],
            'order_by': filter_res['order_by'],
            'order': filter_res['order'],
            'ingredients': [],
            'categories': Ingredient.get_all_ingredients(),
            'results': filter_res['results'],
            'favorites': favorites,
            'user_recipe_list': user_recipes
        }
        return render(request, 'recipes/list.html', context)

    def post(self, request):
        """
        Searches for recipes given a search query
        :param request:
        """
        filter_res = _filter_recipes(
            request.POST.get('ingredients'),
            request.POST.get('query'),
            request.POST.get('limit'),
            request.POST.get('order_by'),
            request.POST.get('order'),
            request.POST.get('page')
        )

        favorites = None

        if request.user.is_authenticated():
            profile = UserProfile.get_or_create_profile(request.user)
            favorites = profile.get_favorites()

        context = {
            'query': filter_res['query'],
            'limit': filter_res['limit'],
            'order_by': filter_res['order_by'],
            'order': filter_res['order'],
            'ingredients': filter_res['ingredients'],
            'categories': Ingredient.get_all_ingredients(),
            'results': filter_res['results'],
            'favorites': favorites

        }
        return render(request, 'recipes/list.html', context)


class RecipeView(View):
    form_class = RecipeForm
    context = {}
    form = None
    recipe_name_message = None
    profile = None
    success_message = None
    recipe_id = None
    get_success_template = None
    post_success_url = None
    post_failure_template = None

    def get(self, request, recipe_id=None):
        self.context = {}
        if recipe_id:
            self.recipe_id = recipe_id
            if not Recipe.objects.filter(pk=recipe_id).exists():
                return redirect(reverse('recipes.search'))
        self.profile = UserProfile.get_or_create_profile(request.user)
        if not self.user_can_access():
            return redirect(reverse('recipes.search'))
        form_init = self.init(request)
        self.form = self.form_class(form_init)
        self.context.update({'form': self.form})

        self.context.update(self.fill_context(request))

        self.recipe_name_message = request.GET.get('success_message', None)

        if self.recipe_name_message:

            self.context['success_message'] = self.recipe_name_message

        return render(request, self.get_success_template, self.context)

    def post(self, request, recipe_id=None):
        self.context = {}
        if recipe_id:
            self.recipe_id = recipe_id
            if not Recipe.objects.filter(pk=recipe_id).exists():
                return redirect(reverse('recipes.search'))
        self.profile = UserProfile.get_or_create_profile(request.user)
        if not self.user_can_access():
            return redirect(reverse('recipes.search'))
        self.init(request)
        self.form = self.form_class(request.POST)

        if self.form.is_valid():
            self.context['form'] = self.form
            try:
                recipe = self.recipe_method()
                success_message = {'success_message': self.success_message.format(recipe.name)}
                query_string = urlencode(success_message)
                return redirect('{}?{}'.format(self.post_success_url, query_string))
            except IntegrityError:
                self.context.update(self.fill_context(request))
                self.context['error_message'] = 'A recipe with that name already exists!'
                return render(request, self.post_failure_template, self.context)
        else:
            self.context['form'] = self.form
            self.context.update(self.fill_context(request))

            return render(request, self.post_failure_template, self.context)

    def fill_context(self, request):
        context = {}
        form = self.context['form']
        categories = form.get_category_fields()
        ingredients = form.get_ingredient_fields()
        qtys = form.get_qty_fields()
        uoms = form.get_uom_fields()
        instructions = form.get_instruction_fields()

        uom_lookup = Ingredient.get_uom_lookup()

        context['ingredient_fields'] = list(zip(categories, ingredients, qtys, uoms))
        context['uom_lookup'] = json.dumps(uom_lookup)
        context['instructions'] = instructions
        context.update(csrf(request))

        return context

    def init(self, request):
        raise NotImplementedError

    def recipe_method(self):
        raise NotImplementedError

    def user_can_access(self):
        raise NotImplementedError


class CreateRecipe(RecipeView):
    form_class = RecipeForm
    success_message = '{} successfully created!'
    get_success_template = 'recipes/recipe_form.html'
    post_success_url = 'recipes.create'
    post_failure_template = 'recipes/recipe_form.html'

    def user_can_access(self):
        return True

    def init(self, request):
        self.context.update({
            'button_type': 'Create',
            'page_title': 'Create a Recipe'
        })
        self.post_success_url = reverse(self.post_success_url)

    def recipe_method(self):
        recipe_name = self.form.get_name()
        instructions = self.form.get_clean_instructions()
        ingredients = self.form.get_clean_ingredients()

        return self.profile.create_recipe(recipe_name, instructions, ingredients)


class EditRecipe(RecipeView):
    form_class = RecipeForm
    success_message = '{} successfully edited!'
    get_success_template = 'recipes/recipe_form.html'
    post_success_url = None
    post_failure_template = 'recipes/recipe_form.html'

    def user_can_access(self):
        recipe_author = Recipe.objects.filter(pk=self.recipe_id).values_list('author', flat=True)[0]
        return self.profile.pk == recipe_author

    def init(self, request):
        self.context.update({
            'button_type': 'Edit',
            'page_title': 'Edit a Recipe',
            'recipe_id': self.recipe_id
        })

        if request.method == 'GET':
            return self.get_init(request)
        elif request.method == 'POST':
            return self.post_init(request)

    def recipe_method(self):
        recipe_name = self.form.get_name()
        instructions = self.form.get_clean_instructions()
        ingredients = self.form.get_clean_ingredients()

        recipe = Recipe.objects.get(pk=self.recipe_id)

        return recipe.edit_recipe(recipe_name, instructions, ingredients)

    def get_init(self, request):
        form_dict = {}
        recipe = Recipe.objects.get(pk=self.recipe_id)
        recipe_ingredients = list(recipe.recipeingredients_set.select_related('ingredient'))
        recipe_instructions = recipe.get_instructions()

        form_dict.update({
            'recipe_name': recipe.name,
            'categories': recipe_ingredients[0].ingredient.category,
            'ingredient': recipe_ingredients[0].ingredient.name,
            'ingredient_qty': recipe_ingredients[0].quantity,
            'uom': recipe_ingredients[0].ingredient.uom,
            'instruction': recipe_instructions[0]
        })

        for i, recipe_ingredient in enumerate(recipe_ingredients[1:], start=1):
            form_dict.update({
                '{}{}'.format(CATEGORY_NAME, i): recipe_ingredient.ingredient.category,
                '{}{}'.format(INGREDIENT_NAME, i): recipe_ingredient.ingredient.name,
                '{}{}'.format(QTY_NAME, i): recipe_ingredient.quantity,
                '{}{}'.format(UOM_NAME, i): recipe_ingredient.ingredient.uom,
            })

        form_dict.update({
            '{}{}'.format(INSTRUCTION_NAME, i): recipe_instruction
            for i, recipe_instruction in enumerate(recipe_instructions[1:], start=1)
        })

        return form_dict

    def post_init(self, request):
        self.post_success_url = reverse('user.profile')


class FavoriteRecipe(View):
    def post(self, request):
        """
        Favorites or Unfavorites a recipe
        :param request:
        """
        if request.is_ajax():
            recipe_id = request.POST.get('recipe_id')
            is_favorite = request.POST.get('is_favorite')

            favorite = False
            if is_favorite == 'true':
                favorite = True

            profile = UserProfile.get_or_create_profile(request.user)
            profile.set_favorites(recipe_id=recipe_id, is_favorite=favorite)

            json_response = {'favorite': favorite }

            return HttpResponse(json.dumps(json_response), content_type='application/json')

        return redirect('recipes.search')   


class RateRecipe(View):
    def post(self, request):
        """
        Rate a recipe
        :param request:
        """
        if request.is_ajax() and request.user.is_authenticated():
            recipe_id = int(request.POST.get('recipe_id'))
            rating = int(request.POST.get('rating'))

            profile = UserProfile.get_or_create_profile(request.user)
            profile.set_rating(recipe_id=recipe_id, rating=rating)

            json_response = {'user-rating': rating }

            return HttpResponse(json.dumps(json_response), content_type='application/json')

        return redirect('recipes.search')


@login_required
def make_drink(request):
    profile = UserProfile.get_or_create_profile(request.user)

    recipe_id = request.POST['recipe']
    made_recipe = Recipe.objects.get(pk=recipe_id)

    recipe_ingredients = made_recipe.get_ingredients()
    recipe_ingredients_ids = recipe_ingredients.keys()

    user_ingredients = list(profile.useringredients_set.filter(
        ingredient_id__in=recipe_ingredients_ids).select_related('ingredient'))

    if len(recipe_ingredients) != len(user_ingredients):
        return HttpResponse('error')

    for user_ingredient in user_ingredients:
        ingredient_id = user_ingredient.ingredient.id
        user_ingredient.quantity -= recipe_ingredients[ingredient_id]
        if user_ingredient.quantity < 0:
            return HttpResponse('error')

    profile.bulk_update_user_ingredient_quantity(user_ingredients)

    return HttpResponse('success')


@login_required()
def delete_recipe(request):

    profile = UserProfile.get_or_create_profile(request.user)

    recipe = request.GET['recipe_name']

    try:
        recipe_id = profile.created_recipes.get(name=recipe).id
    except ObjectDoesNotExist:
        render(request, "user/profile.html", {'error_message': 'This recipe does not exist'})
        return redirect('user.profile')

    profile.delete_recipe(recipe_id)

    return HttpResponse('success')