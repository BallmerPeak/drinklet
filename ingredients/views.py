from django.shortcuts import render, redirect
from django.views.generic import View
from django.core.context_processors import csrf

import json

from .models import Ingredient


class SearchOptions(View):
    def get(self, request):
        """
        Retrieves the list of ingredients and renders the Search page.
        :param request:
        """
        return redirect('recipes.search')
