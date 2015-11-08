from django.conf.urls import include, url
from .views import SearchOptions

urlpatterns = [
    url(r'^$', SearchOptions.as_view(), name='ingredients.search')
]
