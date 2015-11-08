from django.shortcuts import render, redirect
from django.views.generic import View
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
            'error_message': '',
            'success_message': ''
        }
        return render(request, 'recipes/create.html', context)

    def post(self, request):
        """ 
        Creates new recipe 
        """
        recipe_name = request.POST['post_recipe_name']
        print(recipe_name)
        ingredients_id_quantity = request.POST['post_ingredients_id_quantity']
        instructions = request.POST['post_instructions']
        print("recipes.create POST : " + recipe_name + " " + ingredients_id_quantity + " " + instructions)
        return redirect('recipes.create')
