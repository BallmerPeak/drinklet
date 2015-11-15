from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.views.generic import View
from django.core.context_processors import csrf
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.utils.http import urlencode
import json
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist


from .forms.recipes.create_forms import CreateRecipeForm
from .models import Recipe
from .models import RecipeIngredients
from .models import Ingredient
from user.models import UserProfile
from user.models import UserIngredients
from .forms.recipes.forms import RecipeForm


def _filterRecipes(ingredients, query, limit, order, page):
    """
    Build Paginator of results from filtering Recipes
    """
    # Make sure the list contains ids as integers
    try:
        ingredients = list(map(int, ingredients))
    # Invalid list element (probably empty and cant cast int)
    except ValueError:
        ingredients = []

    # If the query is not set, default it to empty
    if query is None:
        query = ""

    # If the limit is not set, default it to 10
    if limit is None:
        limit = 10

    # If the order is not set, default it to asc
    if order is None:
        order = 'asc'

    # If the page is not set, default it to 1
    if page is None:
        page = 1

    # Filter recipes by query in descending order
    if order == 'desc':
        if len(ingredients):
            recipes = sorted(Recipe.get_recipes_by_ingredients(ingredients),key=lambda r:r.name)
        else:
            recipes = Recipe.objects.all().order_by('name')
        recipes = [recipe for recipe in reversed(recipes) if query in recipe.name]
    # Filter recipes by query in ascending order
    else:
        if len(ingredients):
            recipes = sorted(Recipe.get_recipes_by_ingredients(ingredients),key=lambda r:r.name)
        else:
            recipes = Recipe.objects.all().order_by('name')
        recipes = [recipe for recipe in recipes if query in recipe.name]

    paginator = Paginator(recipes,limit)

    # Grab the Recipe objects corresponding to passed in page
    try:
        results = paginator.page(page)
    # Invalid page passed in, give page 1
    except PageNotAnInteger:
        results = paginator.page(1)
    # Invalid page passed in, give page 1
    except EmptyPage:
        results = paginator.page(1)

    # Return all of the values
    return {
        'query': query,
        'limit': limit,
        'order': order,
        'ingredients': ingredients,
        'results': results
    }


class SearchRecipes(View):
    def get(self, request):
        """
        Lists all recipes
        """
        # Create new Paginator object for Recipe objects
        filterRes = _filterRecipes(
            [],
            "",
            request.GET.get('limit'),
            request.GET.get('order'),
            request.GET.get('page')
        )
            
        favorites = None
        if self.request.user.is_authenticated():
            profile = UserProfile.get_or_create_profile(self.request.user)
            favorites = profile.favorites.all()

        context = {
            'query': "",
            'limit': filterRes['limit'],
            'order': filterRes['order'],
            'ingredients': [],
            'categories': Ingredient.get_all_ingredients(),
            'results': filterRes['results'],
            'favorites': favorites
        }
        return render(request, 'recipes/list.html', context)

    def post(self, request):
        """
        Searches for recipes given a search query
        """
        filterRes = _filterRecipes(
            request.POST.get('ingredients').split(','),
            request.POST.get('query'),
            request.POST.get('limit'),
            request.POST.get('order'),
            request.POST.get('page')
        )

        favorites = None

        if self.request.user.is_authenticated():
            profile = UserProfile.get_or_create_profile(self.request.user)
            favorites = profile.favorites.all()

        context = {
            'query': filterRes['query'],
            'limit': filterRes['limit'],
            'order': filterRes['order'],
            'ingredients': filterRes['ingredients'],
            'categories': Ingredient.get_all_ingredients(),
            'results': filterRes['results'],
            'favorites': favorites

        }
        return render(request, 'recipes/list.html', context)


class CreateRecipe(View):
    form_class = CreateRecipeForm
    context = {}

    def get(self, request):
        form = self.form_class(None)
        self.context = {'form': form}

        self.context.update(self.fill_context(request))

        success_recipe_name = request.GET.get('success_message', None)

        if success_recipe_name:
            self.context['success_message'] = '{} successfully created!'.format(success_recipe_name)

        return render(request, 'recipes/create.html', self.context)

    def post(self, request):
        profile = UserProfile.get_or_create_profile(request.user)
        self.context = {}

        def create_recipe():
            recipe_name = form.get_name()
            instructions = form.get_clean_instructions()
            ingredients = form.get_clean_ingredients()

            return profile.create_recipe(recipe_name, instructions, ingredients)

        form = self.form_class(request.POST)

        if form.is_valid():
            self.context['form'] = form
            url_stub = reverse('recipes.create')
            try:
                recipe = create_recipe()
                success_message = {'success_message': recipe.name}
                query_string = urlencode(success_message)
                return redirect('{}?{}'.format(url_stub, query_string))
            except IntegrityError:
                self.context.update(self.fill_context(request))
                self.context['error_message'] = 'A recipe with that name already exists!'
                return render(request, 'recipes/create.html', self.context)
        else:
            self.context['form'] = form
            self.context.update(self.fill_context(request))

            return render(request, 'recipes/create.html', self.context)

    def fill_context(self, request):
        context = {}
        form = self.context['form']
        categories = form.get_category_fields()
        ingredients = form.get_ingredient_fields()
        qtys = form.get_qty_fields()
        uoms = form.get_uom_fields()
        instructions = form.get_instruction_fields()

        uom_lookup = Ingredient.get_uom_lookup()

        context['ingredient_fields'] = list(zip(categories, ingredients, qtys, uoms))
        context['uom_lookup'] = json.dumps(uom_lookup)
        context['instructions'] = instructions
        context.update(csrf(request))

        return context


class FavoriteRecipe(View):
    def post(self, request):
        """
        Favorites or Unfavorites a recipe
        """
        if request.is_ajax():
            recipe_id = request.POST.get('recipe_id')
            is_favorite = request.POST.get('is_favorite')

            favorite = False
            if is_favorite == 'true':
                favorite = True

            profile = UserProfile.get_or_create_profile(self.request.user)
            profile.set_favorites(recipe_id=recipe_id, is_favorite=favorite)

            json_response = {'favorite': favorite }

            return HttpResponse(json.dumps(json_response), content_type='application/json')

        return redirect('recipes.search')   

class RateRecipe(View):
    def post(self, request):
        """
        Rate a recipe
        """
        if request.is_ajax() and self.request.user.is_authenticated():
            recipe_id = int(request.POST.get('recipe_id'))
            rating = int(request.POST.get('rating'))

            profile = UserProfile.get_or_create_profile(self.request.user)
            profile.set_rating(recipe_id=recipe_id, rating=rating)

            json_response = {'user-rating': rating }

            return HttpResponse(json.dumps(json_response), content_type='application/json')

        return redirect('recipes.search')


def MakeDrink(request):
    user = request.user
    quantityUpdates = []
    if user.is_authenticated():
        profile = UserProfile.get_or_create_profile(user)
        for maderecipe in Recipe.objects.all():
            if maderecipe.id == int(request.POST.get("recipe")):
                myrecipe = {"recipe_id": maderecipe.id}
                user_ingredient_ids = []
                for item in UserIngredients.objects.all().values():
                    user_ingredient_ids.append(item.get("ingredient_id"))
                recipe_ingredient_ids = []
                for item in RecipeIngredients.objects.all().values():
                    if item.get("recipe_id") == myrecipe.get("recipe_id"):
                        recipe_ingredient_ids.append(item.get("ingredient_id"))
                if not set(recipe_ingredient_ids).issubset(set(user_ingredient_ids)):
                    return HttpResponse("error")
                for ingredient in RecipeIngredients.objects.all().values():
                    if ingredient.get("recipe_id") == myrecipe.get("recipe_id"):
                        for useringredient in UserIngredients.objects.all().values():
                            if (ingredient.get("ingredient_id") == useringredient.get("ingredient_id")) and (useringredient.get("user_id") == profile.user_id):
                                newQuantity = useringredient.get("quantity") - ingredient.get("quantity")
                                if newQuantity < 0:
                                    return HttpResponse("error")
                                update = {"ingredient_id": ingredient.get("ingredient_id"), "quantity": newQuantity}
                                quantityUpdates.append(update)
        for submission in quantityUpdates:
            profile.update_user_ingredient_quantity(submission.get("ingredient_id"), submission.get("quantity"))
        return HttpResponse("success")


class deleteRecipe(View):
    def post(self,request):
        user = request.user
        result = 0
        if user.is_authenticated:
            recipe = request['recipe_name']
            profile = UserProfile.get_or_create_profile(user)
            try:
                recipe_id = profile.created_recipes.get(name = recipe).id
            except ObjectDoesNotExist:
                render(request,"",{'result':result,'msg':'This recipe does not exist'})

            result = 1
            profile.delete_recipe(recipe_id)

        render(request,"",{'result':result ,'msg':'Successfully deleted'})

class editRecipe(View):
    def get (self ,request):
        user  = request.user
        result = 0
        if user.is_authenticated:
            recipe_name = request['recipe_name']
            profile = UserProfile.get_or_create_profile(user)
            try:
                recipe = profile.created_recipes.get(name = recipe_name)
                recipe_id = recipe.id
            except ObjectDoesNotExist:
                render(request,"",{'result':result,'msg':'The recipe with name %s does not exist'%recipe_name})

            result = 1
            f = RecipeForm(instance = recipe)
            context = {
                'recipeform' : f,
                'exist':result
            }

        return render(request, reverse('recipe.edit'), context)

    def post(self,request):
        user = request.user
        result = 0
        if user.is_authenticated:
            recipe_name = request['recipe_name']
            profile = UserProfile.get_or_create_profile(user)

            extraStep = [value for  key,value in request.items() if key.startswith('xstep')]
            extraIQ = [value for  key,value in request.items() if key.startswith('xiq')]

            try:
                recipe = profile.created_recipes.get(name = recipe_name)
                recipe_id = recipe.id
            except ObjectDoesNotExist:
                render(request,"",{'result':result,'msg':'The recipe with name %s does not exist'%recipe_name})

            f  = RecipeForm(data = request, instance = recipe, extraStep= extraStep,extraIQ=extraIQ)
            if f.is_valid():
                f.save()
                result = 1
            context = {
                'recipeform' : f,
                'success':result
            }

        return render(request, reverse('recipe.edit'), context)

