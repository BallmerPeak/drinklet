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

def _filterRecipes(query, limit, order):
    """
    Build Paginator of results from filtering Recipes
    """
    # If the query is not set, default it to empty
    if query is None:
        query = ""

    # If the limit is not set, default it to 10
    if limit is None:
        limit = 10

    # If the order is not set, default it to asc
    if order is None:
        order = 'asc'

    # Filter recipes by query in descending order
    if order == 'desc':
        recipes = Recipe.objects.extra(
                select={'lower_name': 'lower(name)'}
            ).filter(name__iregex=r''+query).order_by('-lower_name')
    # Filter recipes by query in ascending order
    else:
        recipes = Recipe.objects.extra(
                select={'lower_name': 'lower(name)'}
            ).filter(name__iregex=r''+query).order_by('lower_name')

    # Return all of the values
    return {
        'query': query,
        'limit': limit,
        'order': order,
        'paginator': Paginator(recipes,limit)
    }


class SearchRecipesByName(View):
    def get(self, request):
        return redirect('recipes.list')

    def post(self, request):
        """
        Searches for recipes given a search query
        """
        filterRes = _filterRecipes(
            request.POST.get('query'),
            request.POST.get('limit'),
            request.POST.get('order')
        )

        favorites = None

        if self.request.user.is_authenticated():
            profile = UserProfile.get_or_create_profile(self.request.user)
            favorites = profile.favorites.all()

        context = {
            'limit': filterRes['limit'],
            'order': filterRes['order'],
            'query': filterRes['query'],
            'results': filterRes['paginator'].page(1),
            'favorites': favorites
        }
        return render(request, 'recipes/list.html', context)

class SearchRecipesByIngredients(View):
    def get(self, request):
        return redirect('ingredients.search')

    def post(self, request):
        """
        Searches for recipes given a list of ingredients
        """
        print("InPOST")
        ingredient_ids = json.loads(request.POST['ingredient_ids'])
        favorites = None
        if not self.request.user.is_anonymous():
            useringredients = list(UserProfile.get_or_create_profile(self.request.user).ingredients.values_list('id', flat=True))
            ingredientstoremove = list(set(useringredients) - set(ingredient_ids))
            ingredientstoadd = list(set(ingredient_ids) - set(useringredients))
            for ingredient in ingredientstoremove:
                self.request.user.userprofile.delete_user_ingredient(ingredient)
            if len(ingredientstoadd) > 0:
                self.request.user.userprofile.add_user_ingredients(ingredientstoadd)

        if self.request.user.is_authenticated():
            profile = UserProfile.get_or_create_profile(self.request.user)
            favorites = profile.favorites.all()

        context = {
            'results': Recipe.get_recipes_by_ingredients(ingredient_ids),
            'favorites': favorites,
            'parameters': []
        }
        for i in ingredient_ids:
            context['parameters'].append(Ingredient.objects.get(id=i))
        return render(request, 'recipes/index.html', context)
    

class ListRecipes(View):
    def get(self, request):
        """
        Lists all recipes
        """
        # Create new Paginator object for Recipe objects
        filterRes = _filterRecipes(
            "",
            request.GET.get('limit'),
            request.GET.get('order')
        )
        paginator = filterRes['paginator']    
        page = request.GET.get('page')
        # Grab the Recipe objects corresponding to passed in page
        try:
            results = paginator.page(page)
        # Invalid page passed in, give page 1
        except PageNotAnInteger:
            results = paginator.page(1)
        # Invalid page passed in, give page 1
        except EmptyPage:
            results = paginator.page(1)
            
        favorites = None
        if self.request.user.is_authenticated():
            profile = UserProfile.get_or_create_profile(self.request.user)
            favorites = profile.favorites.all()

        context = {
            'limit': filterRes['limit'],
            'order': filterRes['order'],
            'query': "",
            'results': results,
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

        return redirect('recipes.list')

def MakeDrink(request):
    user = request.user
    if user.is_authenticated():
        profile = UserProfile.get_or_create_profile(user)
        for maderecipe in Recipe.objects.all():
            if maderecipe.id == int(request.POST.get("recipe")):
                myrecipe = {"recipe_id": maderecipe.id, "ingredients": maderecipe.ingredients.values()}
                for ingredient in RecipeIngredients.objects.all().values():
                    if ingredient.get("recipe_id") == myrecipe.get("recipe_id"):
                        for useringredient in UserIngredients.objects.all().values():
                            if (ingredient.get("ingredient_id") == useringredient.get("ingredient_id")) and (useringredient.get("user_id") == profile.user_id):
                                newQuantity = useringredient.get("quantity") - ingredient.get("quantity")
                                if newQuantity < 0:
                                    newQuantity = 0
    return HttpResponse("success")
