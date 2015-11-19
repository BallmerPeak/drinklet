from django.contrib import admin
from .models import Recipe, RecipeIngredients

admin.site.register(Recipe)
admin.site.register(RecipeIngredients)