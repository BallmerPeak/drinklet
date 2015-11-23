from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.views import AuthenticationForm
from django.views.generic import View
from user import forms
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render
from user.models import UserProfile
from user.models import UserIngredients
from ingredients.models import Ingredient

import json

# Create your views here.


class Register(View):

    def post(self, request):
        form = forms.RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username').lower()
            password = form.cleaned_data.get('pwd')
            email = form.cleaned_data.get('email')
            User.objects.create_user(username, email, password)
            user = authenticate(username=username, password=password)
            login(request,user)
            return HttpResponseRedirect(reverse('recipes.search'))
        else:
            return render(request, 'recipes/list.html', {'form': form})


class Profile(View):
    def get(self, request):
        user = self.request.user
        if user.is_authenticated():
            profile = UserProfile.get_or_create_profile(user)
            ingredients = profile.ingredients.values()
            ingredientQuantity = []
            for e in ingredients:
                for ingredient in UserIngredients.objects.all().values():
                    id = ingredient.get("ingredient_id")
                    if id == e.get("id"):
                        item = {"id": id, "name": e.get("name"), "quantity": ingredient.get("quantity")}
                        ingredientQuantity.append(item)
            favorites = profile.favorites.all()
            context = {
                'profile': profile,
                'userIngredients': ingredientQuantity,
                'favorites': favorites
            }
            return render(request, 'user/profile.html', context)
        return HttpResponseRedirect(reverse('recipes.search'))

    def post(self, request):
        user = self.request.user
        if user.is_authenticated():
            profile = UserProfile.get_or_create_profile(user)

            quantities = json.loads(request.POST["ingredient_objects"])
            deleted = json.loads(request.POST["deleted_ingredients"])
            for removedIngredient in deleted:
                profile.delete_user_ingredient(removedIngredient.get("id"))

            ingredients = profile.ingredients.values()
            ingredientQuantity = []
            for e in ingredients:
                for ingredient in UserIngredients.objects.all().values():
                    id = ingredient.get("ingredient_id")
                    if id == e.get("id"):
                        item = {"id": id, "name": e.get("name"), "quantity": ingredient.get("quantity")}
                        ingredientQuantity.append(item)
            favorites = profile.favorites.all()
            context = {
                'profile': profile,
                'userIngredients': ingredientQuantity,
                'favorites': favorites
            }
            return render(request, 'user/profile.html', context)
        return HttpResponseRedirect(reverse('recipes.search'))


class Login(View):
    form = AuthenticationForm()

    def get(self, request):
        return render(request, 'user/login.html', {'form': self.form})

    def post(self, request):
        self.form = AuthenticationForm(None, request.POST)
        if self.form.is_valid():
            login(request, self.form.get_user())
            return render(request, 'navbar.html')

        context = {
            'form': self.form,
            'username': self.form.cleaned_data.get('username')
        }
        return HttpResponse(render(request, 'user/login.html', context), status=401)


def logout_view(request):
    logout(request)

    return HttpResponseRedirect(reverse('recipes.search'))


