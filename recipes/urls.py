from django.conf.urls import include, url
from .views import ListRecipes, CreateRecipe, SearchRecipesByName, SearchRecipesByIngredients, MakeDrink

urlpatterns = [
	url(r'^$', ListRecipes.as_view(), name='recipes.list'),
	url(r'^create/$', CreateRecipe.as_view(), name='recipes.create'),
	url(r'^search/name/$', SearchRecipesByName.as_view(), name='recipes.name'),
	url(r'^search/ingredients/$', SearchRecipesByIngredients.as_view(), name='recipes.ingredients'),
	url(r'^makedrink', MakeDrink, name='recipes.makedrink')
]