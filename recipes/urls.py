from django.conf.urls import include, url
from .views import CreateRecipe, SearchRecipes, FavoriteRecipe

urlpatterns = [
	url(r'^$', SearchRecipes.as_view(), name='recipes.search'),
	url(r'^create/$', CreateRecipe.as_view(), name='recipes.create'),
	url(r'^favorite/$', FavoriteRecipe.as_view(), name='recipes.favorite'),
]