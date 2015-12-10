from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from .views import Register, Profile, Login, logout_view, change_password

urlpatterns = [
    url(r'^register$', Register.as_view(), name='user.register'),
    url(r'^login$', Login.as_view(), name='user.login'),
    url(r'^logout$', logout_view, name='user.logout'),
    url(r'^profile$', login_required(Profile.as_view()), name='user.profile'),
    url(r'^change-password$', change_password, name='profile.change_password'),
]
