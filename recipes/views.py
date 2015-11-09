from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.views.generic import View
from django.core.context_processors import csrf
import json

from .models import Recipe
from .models import Ingredient
from user.models import UserProfile


class SearchRecipes(View):
    def get(self, request):
        return redirect('ingredients.search')

    def post(self, request):
        """
        Searches for recipes given a list of ingredients
        """
        print("InPOST")
        ingredient_ids = json.loads(request.POST['ingredient_ids'])
        if not self.request.user.is_anonymous():
            useringredients = list(UserProfile.get_or_create_profile(self.request.user).ingredients.values_list('id', flat=True))
            ingredientstoremove = list(set(useringredients) - set(ingredient_ids))
            ingredientstoadd = list(set(ingredient_ids) - set(useringredients))
            for ingredient in ingredientstoremove:
                self.request.user.userprofile.delete_user_ingredient(ingredient)
            if len(ingredientstoadd) > 0:
                self.request.user.userprofile.add_user_ingredients(ingredientstoadd)
        context = {
            'results': Recipe.get_recipes_by_ingredients(ingredient_ids),
            'parameters': []
        }
        for i in ingredient_ids:
            context['parameters'].append(Ingredient.objects.get(id=i))
        return render(request, 'recipes/index.html', context)

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