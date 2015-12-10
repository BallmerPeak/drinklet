from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect

# Create your views here.


@login_required
def get_notifications(request):
    if not request.is_ajax():
        return redirect(reverse('recipes.search'))

    return render(request, 'notifications/notification-ajax.html')

