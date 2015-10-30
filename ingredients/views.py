from django.shortcuts import render

from .models import Ingredient

def index(request):
    """
    Retrieves the list of ingredients and renders the Ingredients page.
    """
    context = {
        'ingredients': Ingredient.objects.all(),
    }
    return render(request, 'ingredients/index.html', context)