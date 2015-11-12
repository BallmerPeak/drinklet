from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from .views import CreateRecipe, SearchRecipes, FavoriteRecipe, RateRecipe, MakeDrink

urlpatterns = [
    url(r'^$', SearchRecipes.as_view(), name='recipes.search'),
    url(r'^create/$', login_required(CreateRecipe.as_view()), name='recipes.create'),
    url(r'^favorite/$', FavoriteRecipe.as_view(), name='recipes.favorite'),
    url(r'^rate/$', RateRecipe.as_view(), name='recipes.rate'),
    url(r'^makedrink', MakeDrink, name='recipes.makedrink'),
]
