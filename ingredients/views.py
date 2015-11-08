from django.shortcuts import render
from django.views.generic import View
from user.models import UserProfile
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
    def post(self, request):
        """
        Adds selected ingredients to ingredient list
        """
        ingredients = request.POST.getlist('selectedIngredients')
        profile = UserProfile.get_or_create_profile(self.request.user)
        test = list(profile.ingredients.values_list('id', flat=True))
        uniqueingredients = list(set(ingredients + test))
        #UserProfile.get_or_create_profile(self.request.user).add_user_ingredients(uniqueingredients)
        ingredientTest = self.request.user.userprofile.add_user_ingredients(uniqueingredients)
        userIngredientsJSON = {}
        for useringredient in ingredientTest.keys():
            userIngredientsJSON[useringredient] = useringredient

        ingredientsJSON = {}
        for ingredient in Ingredient.objects.all().values():
            ingredientsJSON[ingredient['id']] = ingredient
        context = {
            'userIngredientsJSON': json.dumps(userIngredientsJSON),
            'categories': Ingredient.get_all_ingredients(),
            'ingredientsJSON': json.dumps(ingredientsJSON)
        }
        return render(request, 'ingredients/index.html', context)
