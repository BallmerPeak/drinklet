from django.conf.urls import url
from .views import Register, Profile, Login, logout_view

urlpatterns = [
    url(r'^register$', Register.as_view(), name='user.register'),
    url(r'^login$', Login.as_view(), name='user.login'),
    url(r'^logout$', logout_view, name='user.logout'),
    url(r'^profile$', Profile.as_view(), name='user.profile')
]
