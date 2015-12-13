from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.views import AuthenticationForm, password_change, password_change_done
from django.views.generic import View
from user import forms
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from user.models import UserProfile
from ingredients.models import Ingredient
from django.contrib.auth import update_session_auth_hash

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
            UserProfile.get_or_create_profile(user)
            login(request, user)

            redirect_info = {
                'redirect': reverse('user.profile')
            }
            return HttpResponse(json.dumps(redirect_info))
        else:
            return HttpResponse(render(request, 'user/register.html', {'form': form}), status=401)


class Profile(View):
    def get(self, request):
        profile = UserProfile.get_or_create_profile(request.user)
        messages = []
        recipe_edit_success_message = request.GET.get('success_message', '')
        if recipe_edit_success_message:
            messages.append(recipe_edit_success_message)

        user_ingredients = profile.useringredients_set.select_related('ingredient')
        ingredient_quantity = [
            {
                'id': user_ingredient.ingredient_id,
                'name': user_ingredient.ingredient.name,
                'quantity': user_ingredient.quantity,
                'uom': user_ingredient.ingredient.uom
            }
            for user_ingredient in user_ingredients
        ]

        favorites = profile.get_favorites()

        # Get list of ids corresponding to user's ingredients
        user_ingredient_ids = profile.ingredients.values_list('id', flat=True)

        # Get a category bucketed list of ingredients that the user does not have
        unowned_ingredients = Ingredient.objects.exclude(pk__in=user_ingredient_ids)
        ingredient_categories = unowned_ingredients.values_list('category', flat=True).distinct()

        categories = {
            category: unowned_ingredients.filter(category=category)
            for category in ingredient_categories
        }

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

        return redirect(reverse('user.profile'))


def change_password(request):
    u = User.objects.get(username=request.user)
    oldPwd = request.POST['oldpwd']
    newPwd = request.POST['newpwd']
    confirmPwd = request.POST['confirmpwd']

    if not User.check_password(u, oldPwd):
        return HttpResponse("Your old password was entered incorrectly. "
                                "Please enter it again.", status=401)
    if not newPwd == confirmPwd:
        return HttpResponse("The two password fields didn't match.", status=401)

    if newPwd == "" or oldPwd == "" or confirmPwd == "":
        return HttpResponse("You cannot have an empty password", status=401)

    if newPwd == oldPwd or confirmPwd == oldPwd:
        return HttpResponse("You cannot change to the same password", status=401)

    if User.check_password(u, oldPwd) and newPwd == confirmPwd:
        User.set_password(u, newPwd)
        u.save()
        update_session_auth_hash(request, u)
    pwsuccess = {
        'redirect': reverse('user.profile')
    }
    return HttpResponse(json.dumps(pwsuccess))


class Login(View):
    form = AuthenticationForm()

    def get(self, request):
        return render(request, 'user/login.html', {'form': self.form})

    def post(self, request):
        self.form = AuthenticationForm(None, request.POST)
        if self.form.is_valid():
            login(request, self.form.get_user())
            redirect_info = {
                'redirect': reverse('user.profile')
            }
            return HttpResponse(json.dumps(redirect_info))

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






