from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from .views import CreateRecipe, SearchRecipes, FavoriteRecipe, RateRecipe, MakeDrink,editRecipe,deleteRecipe

urlpatterns = [
    url(r'^$', SearchRecipes.as_view(), name='recipes.search'),
    url(r'^create/$', login_required(CreateRecipe.as_view()), name='recipes.create'),
    url(r'^favorite/$', FavoriteRecipe.as_view(), name='recipes.favorite'),
    url(r'^rate/$', RateRecipe.as_view(), name='recipes.rate'),
    url(r'^makedrink', MakeDrink, name='recipes.makedrink'),
    url(r'^edit/$',login_required(editRecipe.as_view()),name='recipes.edit'),
    url(r'^delete/$',login_required(deleteRecipe), name='recipes.delete')

]

