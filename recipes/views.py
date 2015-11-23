from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.views.generic import View
from django.core.context_processors import csrf
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
import json

from .models import Recipe
from .models import Ingredient
from user.models import UserProfile

def _filterRecipes(ingredients, query, limit, order, page):
    """
    Build Paginator of results from filtering Recipes
    """
    # Make sure the list contains ids as integers
    try:
        ingredients = list(map(int,ingredients))
    # Invalid list element (probably empty and cant cast int)
    except ValueError:
        ingredients = []

    # If the query is not set, default it to empty
    if query is None:
        query = ""

    # If the limit is not set, default it to 10
    if limit is None:
        limit = 10

    # If the order is not set, default it to asc
    if order is None:
        order = 'asc'

    # If the page is not set, default it to 1
    if page is None:
        page = 1

    # Filter recipes by query in descending order
    if order == 'desc':
        if len(ingredients):
            recipes = Recipe.objects.extra(
                    select={'lower_name': 'lower(name)'}
                ).filter(ingredients__id__in=ingredients, name__iregex=r''+query).distinct().order_by('-lower_name')
        else:
            recipes = Recipe.objects.extra(
                    select={'lower_name': 'lower(name)'}
                ).filter(name__iregex=r''+query).order_by('-lower_name')
    # Filter recipes by query in ascending order
    else:
        if len(ingredients):
            recipes = Recipe.objects.extra(
                    select={'lower_name': 'lower(name)'}
                ).filter(ingredients__id__in=ingredients, name__iregex=r''+query).distinct().order_by('lower_name')
        else:
            recipes = Recipe.objects.extra(
                    select={'lower_name': 'lower(name)'}
                ).filter(name__iregex=r''+query).order_by('lower_name')

    paginator = Paginator(recipes,limit)

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
        'order': order,
        'ingredients': ingredients,
        'results': results
    }

class SearchRecipes(View):
    def get(self, request):
        """
        Lists all recipes
        """
        # Create new Paginator object for Recipe objects
        filterRes = _filterRecipes(
            [],
            "",
            request.GET.get('limit'),
            request.GET.get('order'),
            request.GET.get('page')
        )
            
        favorites = None
        if self.request.user.is_authenticated():
            profile = UserProfile.get_or_create_profile(self.request.user)
            favorites = profile.favorites.all()

        context = {
            'query': "",
            'limit': filterRes['limit'],
            'order': filterRes['order'],
            'ingredients': [],
            'categories': Ingredient.get_all_ingredients(),
            'results': filterRes['results'],
            'favorites': favorites
        }
        return render(request, 'recipes/list.html', context)

    def post(self, request):
        """
        Searches for recipes given a search query
        """
        filterRes = _filterRecipes(
            request.POST.get('ingredients').split(','),
            request.POST.get('query'),
            request.POST.get('limit'),
            request.POST.get('order'),
            request.POST.get('page')
        )

        favorites = None

        if self.request.user.is_authenticated():
            profile = UserProfile.get_or_create_profile(self.request.user)
            favorites = profile.favorites.all()

        context = {
            'query': filterRes['query'],
            'limit': filterRes['limit'],
            'order': filterRes['order'],
            'ingredients': filterRes['ingredients'],
            'categories': Ingredient.get_all_ingredients(),
            'results': filterRes['results'],
            'favorites': favorites
        }
        return render(request, 'recipes/list.html', context)

class CreateRecipe(View):
    def get(self, request):
        """
        Retrieves the list of ingredients and renders
        the form to Create a recipe.
        """
        context = {
            'categories': Ingredient.get_all_ingredients(),
            'error_message': request.GET.get('error_message', ''),
            'success_message': request.GET.get('success_message', '')
        }

        context.update(csrf(request))
        return render(request, 'recipes/create.html', context)

    def post(self, request):
        """ 
        Creates new recipe 
        """
        recipe_name = request.POST['post_recipe_name']
        ingredients_id_quantity = json.loads(request.POST['post_ingredients_id_quantity'])
        instructions_array = json.loads(request.POST['post_instructions'])

        error = ''
        success = ''

        try:
           Recipe._add_recipe(name=recipe_name, instructions=instructions_array, ingredients_info=ingredients_id_quantity)
        except IntegrityError as e:
            error = 'There is already a recipe by the name of ' + recipe_name + '.'
        else:
            success = 'Successfully created ' + recipe_name + '.'

        context = {
            'categories': Ingredient.get_all_ingredients(),
            'error_message': error,
            'success_message': success
        }

        return render(request, 'recipes/create.html', context)

class FavoriteRecipe(View):
    def post(self, request):
        """
        Favorites or Unfavorites a recipe
        """
        if request.is_ajax():
            recipe_id = request.POST.get('recipe_id')
            is_favorite = request.POST.get('is_favorite')

            favorite = False
            if is_favorite:
                favorite = True

            profile = UserProfile.get_or_create_profile(self.request.user)
            profile.set_favorites(recipe_id=recipe_id, is_favorite=favorite)

            json_response = {'favorite': favorite }

            return HttpResponse(json.dumps(json_response), content_type='application/json')

        return redirect('recipes.search')   
