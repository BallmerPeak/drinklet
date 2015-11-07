from django.conf.urls import include, url
from .views import Register

urlpatterns = [
	url(r'^$', Register.as_view(), name='user.register')
]