from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import login,authenticate
from django.views.generic import View
from user import forms
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render
from user.models import UserProfile
# Create your views here.

class Register(View ):

    def post(self, request):
        form = forms.RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('pwd')
            email = form.cleaned_data.get('email')
            User.objects.create_user(username, email, password)
            user = authenticate(username=username, password=password)
            login(request,user)
            return  HttpResponseRedirect(reverse('ingredients.search'))
        else:
            return render(request,'ingredients/index.html', {'form':form})



class Profile(View):
    def get(self,request):
        user = self.request.user
        if (user.is_authenticated()):
            profile = UserProfile.create_or_get_profile(user)