from django.shortcuts import redirect
from django.views.generic import View

from user.models import UserProfile


class AddIngredients(View):
    def get(self, request):
        return redirect('recipes.search')

    def post(self, request):
        """
        Adds ingredients to user's list of ingredients
        """
        # Make sure user is authenticated
        if not self.request.user.is_anonymous():
            ingredient_ids = request.POST.get('add_ingredients').split(',')
            # Make sure the list contains ids as integers
            try:
                ingredient_ids = list(map(int,ingredient_ids))
            # Invalid list element (probably empty and cant cast int)
            except ValueError:
                ingredient_ids = []

            # Grab the user's list of ingredients
            useringredients = list(UserProfile.get_or_create_profile(self.request.user).ingredients.values_list('id', flat=True))

            # Grab the ingredients the user doesn't have
            ingredientstoadd = list(set(ingredient_ids) - set(useringredients))

            # If there are ingredients the user doesn't have, add them
            if len(ingredientstoadd) > 0:
                self.request.user.userprofile.add_user_ingredients(ingredientstoadd)
            return redirect('user.profile')
        return redirect('recipes.search')
