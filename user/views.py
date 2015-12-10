from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.views import AuthenticationForm, password_change, password_change_done
from django.views.generic import View
from user import forms
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render
from user.models import UserProfile
from user.models import UserIngredients
from ingredients.models import Ingredient

import json
from django.core.exceptions import ObjectDoesNotExist


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
            UserProfile.get_or_create_profile(user)
            login(request, user)

            return render(request, 'navbar.html')
        else:
            return HttpResponse(render(request, 'user/register.html', {'form': form}), status=401)


class Profile(View):
    def get(self, request):
        profile = UserProfile.get_or_create_profile(request.user)
        messages = []
        recipe_edit_success_message = request.GET.get('success_message', '')
        if recipe_edit_success_message:
            messages.append(recipe_edit_success_message)
        ingredients = profile.ingredients.values()
        ingredient_quantity = []
        for e in ingredients:
            for ingredient in UserIngredients.objects.all().values():
                id = ingredient.get("ingredient_id")
                if id == e.get("id"):
                    item = {"id": id, "name": e.get("name"), "quantity": ingredient.get("quantity")}
                    ingredient_quantity.append(item)
        favorites = profile.get_favorites()

        # Get list of ids corresponding to user's ingredients
        user_ingredient_ids = profile.ingredients.values_list('id', flat=True)

        # Get a category bucketed list of ingredients that the user does not have
        categories = {}
        for category, category_ingredients in Ingredient.get_all_ingredients().items():
            categories[category] = []
            for ingredient in  category_ingredients:
                if(not ingredient.id in user_ingredient_ids):
                    categories[category].append(ingredient)
        user_recipes = profile.get_all_recipes()

        context = {
            'profile': profile,
            'categories': categories,
            'user_ingredients': ingredient_quantity,
            'search_ingredients': ','.join([str(ingredient) for ingredient in user_ingredient_ids]),
            'add_ingredients': user_ingredient_ids,
            'favorites': favorites,
            'messages': messages,
            'user_recipe_list': user_recipes
        }
        return render(request, 'user/profile.html', context)

    def post(self, request):
        profile = UserProfile.get_or_create_profile(request.user)

        quantities = json.loads(request.POST["ingredient_objects"])
        deleted = json.loads(request.POST["deleted_ingredients"])
        for removedIngredient in deleted:
            profile.delete_user_ingredient(removedIngredient.get("id"))

        user_ingredient_info = {
            info['id']: info['quantity']
            for info in quantities
        }
        user_ingredients_ids = user_ingredient_info.keys()
        user_ingredients = list(profile.useringredients_set.filter(
            ingredient_id__in=user_ingredients_ids).select_related('ingredient'))

        for user_ingredient in user_ingredients:
            ingredient_id = user_ingredient.ingredient_id
            user_ingredient.quantity = user_ingredient_info[ingredient_id]

        profile.bulk_update_user_ingredient_quantity(user_ingredients)

        ingredients = profile.ingredients.values()
        ingredient_quantity = []
        for e in ingredients:
            for ingredient in UserIngredients.objects.all().values():
                ingredient_id = ingredient.get("ingredient_id")
                if ingredient_id == e.get("id"):
                    item = {"id": ingredient_id, "name": e.get("name"), "quantity": ingredient.get("quantity")}
                    ingredient_quantity.append(item)
        favorites = profile.get_favorites()

        # Get list of ids corresponding to user's ingredients
        user_ingredient_ids = profile.ingredients.values_list('id', flat=True)

        # Get a category bucketed list of ingredients that the user does not have
        categories = {}
        for category, category_ingredients in Ingredient.get_all_ingredients().items():
            categories[category] = []
            for ingredient in category_ingredients:
                if ingredient.id not in user_ingredient_ids:
                    categories[category].append(ingredient)

        context = {
            'profile': profile,
            'categories': categories,
            'user_ingredients': ingredient_quantity,
            'search_ingredients': ','.join([str(ingredient) for ingredient in user_ingredient_ids]),
            'add_ingredients': list(profile.ingredients.values_list('id', flat=True)),
            'favorites': favorites
        }
        return render(request, 'user/profile.html', context)


def change_password(request):
    u = User.objects.get(username=request.user)
    if not User.check_password(u, request.POST['pwd']):
        return HttpResponse('error', status=401)
    if User.check_password(u, request.POST['pwd']) and request.POST['pwd2'] == request.POST['pwd3']:
            newpwd = "blah"
    return HttpResponse('error')


class Login(View):
    form = AuthenticationForm()

    def get(self, request):
        return render(request, 'user/login.html', {'form': self.form})

    def post(self, request):
        self.form = AuthenticationForm(None, request.POST)
        if self.form.is_valid():
            login(request, self.form.get_user())
            redirect = {
                'redirect': reverse('user.profile')
            }
            return HttpResponse(json.dumps(redirect))

        context = {
            'form': self.form
        }
        username = self.form.cleaned_data.get('username', None)
        if username:
            context['username'] = username

        return HttpResponse(render(request, 'user/login.html', context), status=401)


def logout_view(request):
    logout(request)

    return HttpResponseRedirect(reverse('recipes.search'))






