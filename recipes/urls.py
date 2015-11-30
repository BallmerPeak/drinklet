from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from .views import CreateRecipe, SearchRecipes, FavoriteRecipe, RateRecipe, make_drink, EditRecipe, delete_recipe

urlpatterns = [
    url(r'^$', SearchRecipes.as_view(), name='recipes.search'),
    url(r'^create/$', login_required(CreateRecipe.as_view()), name='recipes.create'),
    url(r'^favorite/$', FavoriteRecipe.as_view(), name='recipes.favorite'),
    url(r'^rate/$', RateRecipe.as_view(), name='recipes.rate'),
    url(r'^makedrink', make_drink, name='recipes.makedrink'),
    url(r'^edit/(?P<recipe_id>[0-9]+)/$', login_required(EditRecipe.as_view()), name='recipes.edit'),
    url(r'^delete/$', delete_recipe, name='recipes.delete'),
]
