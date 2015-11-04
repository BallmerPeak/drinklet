from django.shortcuts import render
from django.views.generic import View
import json

from .models import Ingredient

class SearchOptions(View):
    def get(self, request):
        """
        Retrieves the list of ingredients and renders the Search page.
        """
        ingredientsJSON = {}
        for ingredient in Ingredient.objects.all().values():
            ingredientsJSON[ingredient['id']] = ingredient
        context = {
            'categories': Ingredient.get_all_ingredients(),
            'ingredientsJSON': json.dumps(ingredientsJSON)
        }
        return render(request, 'ingredients/index.html', context)