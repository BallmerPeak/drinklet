from django.conf.urls import include, url
from .views import SearchRecipes, CreateRecipe

urlpatterns = [
	url(r'^$', SearchRecipes.as_view(), name='recipes.search'),
	url(r'^create/$', CreateRecipe.as_view(), name='recipes.create'),
]