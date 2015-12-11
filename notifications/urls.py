from django.conf.urls import url
from .views import get_notifications

urlpatterns = [
    url(r'^$', get_notifications, name='notifications.get'),
]
