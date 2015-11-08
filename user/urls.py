from django.conf.urls import url
from .views import Register, Login, logout_view

urlpatterns = [
    url(r'^$', Register.as_view(), name='user.register'),
    url(r'^login$', Login.as_view(), name='user.login'),
    url(r'^logout$', logout_view, name='user.logout')
]
