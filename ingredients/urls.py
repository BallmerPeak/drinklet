from django.conf.urls import include, url
from django.contrib.auth.decorators import login_required
from .views import AddIngredients

urlpatterns = [
	url(r'^add/$', login_required(AddIngredients.as_view()), name='ingredients.add'),
]