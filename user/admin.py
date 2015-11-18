from django.contrib import admin
from .models import UserProfile, UserRecipeRating, UserIngredients, RecipeComment

admin.site.register(UserProfile)
admin.site.register(UserRecipeRating)
admin.site.register(UserIngredients)
admin.site.register(RecipeComment)