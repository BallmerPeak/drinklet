from django.shortcuts import render, redirect
from django.views.generic import View
import json

from .models import Recipe


class SearchRecipes(View):
    def get(self, request):
        return redirect('ingredients.search')

    def post(self, request):
        """
        Searches for recipes given a list of ingredients
        """
        ingredient_ids = json.loads(request.POST['ingredient_ids'])
        context = {
            'results': Recipe.get_recipes_by_ingredients(ingredient_ids)
        }
        return render(request, 'recipes/index.html', context)