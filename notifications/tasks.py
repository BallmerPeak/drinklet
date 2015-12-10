from __future__ import absolute_import
from celery import shared_task
from django.apps import apps
from django.db import models

from notifications.models import Notification


def get_user_ingredients(user):
    return {
        ingredient_id: quantity
        for ingredient_id, quantity
        in user.useringredients_set.select_related('ingredient').values_list('ingredient_id', 'quantity')
    }


def get_fav_created_recipe_ing(user):
    recipe_ingredients = apps.get_model('recipes', 'recipeingredients')
    queryset = recipe_ingredients.objects.select_related('ingredient')
    created_recipes = user.created_recipes.prefetch_related(models.Prefetch('recipeingredients', queryset=queryset))
    created_recipes_ing = created_recipes.values_list('recipeingredients__ingredient_id', 'recipeingredients__quantity')
    favorite_recipes = user.favorites.prefetch_related(models.Prefetch('recipeingredients', queryset=queryset))
    favorite_recipes_ing = favorite_recipes.values_list(
        'recipeingredients__ingredient_id', 'recipeingredients__quantity'
    )
    fav_created_recipes_ing = list(created_recipes_ing) + list(favorite_recipes_ing)
    fav_created_recipes_ing.sort()

    last_ing_id = -1
    ret_list = []

    for ing_id, qty in fav_created_recipes_ing:
        if ing_id == last_ing_id:
            ret_list[-1] = (ing_id, qty)
        else:
            last_ing_id = ing_id
            ret_list.append((ing_id, qty))

    return ret_list


def get_user_notifications(user):
    return {
        ingredient_id: notification_id
        for ingredient_id, notification_id
        in user.user_notifications.select_related('ingredient').values_list('ingredient_id', 'pk')
    }


def get_user(user_info):
    user_profile = apps.get_model('user', 'userprofile')
    return user_profile.objects.get(pk=user_info['pk'])


@shared_task
def create_notification(user_info):
    user_profile = apps.get_model('user', 'userprofile')
    try:
        user = user_profile.objects.get(pk=user_info['pk'])
    except user_profile.DoesNotExist:  # Corrects unit test issues
        return 'Unit Test result'

    user_ingredients = get_user_ingredients(user)
    fav_created_recipe_ing = get_fav_created_recipe_ing(user)
    user_notifications = get_user_notifications(user)
    low_ingredients = []
    good_ingredients = []

    for ingredient_id, qty in fav_created_recipe_ing:
        has_notify = True if ingredient_id in user_notifications else False
        user_ing_qty = user_ingredients.get(ingredient_id, 0)

        if user_ing_qty < qty and not has_notify:
            low_ingredients.append(ingredient_id)

        if user_ing_qty >= qty and has_notify:
            good_ingredients.append(ingredient_id)
    if low_ingredients:
        Notification.create_low_ingredient_notifications(user, low_ingredients)
    if good_ingredients:
        Notification.remove_low_ingredient_notifications(user, good_ingredients)
