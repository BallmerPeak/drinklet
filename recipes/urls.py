from django.conf.urls import include, url
from .views import SearchRecipes

urlpatterns = [
	url(r'^$', SearchRecipes.as_view(), name='recipes.search')
]