from django.conf.urls import include, url
from .views import SearchRecipes, CreateRecipe, ListRecipes

urlpatterns = [
	url(r'^$', SearchRecipes.as_view(), name='recipes.search'),
	url(r'^create/$', CreateRecipe.as_view(), name='recipes.create'),
	url(r'^list/$', ListRecipes.as_view(), name='recipes.list')
]