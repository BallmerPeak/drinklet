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
from django.contrib import messages


from .forms.recipes.create_forms import CreateRecipeForm
from .models import Recipe
from .models import RecipeIngredients
from .models import Ingredient
from user.models import UserProfile
from user.models import UserIngredients
from .forms.recipes.forms import RecipeForm


def _filterRecipes(ingredients, query, limit, order, page, user=None):
    """
    Build Paginator of results from filtering Recipes
    """
    # Get Recipe calling object
    call_object = Recipe if user is None else user
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
        limit = 6

    # If the order is not set, default it to asc
    if order is None:
        order = 'asc'

    # If the page is not set, default it to 1
    if page is None:
        page = 1

    # Filter recipes by query in descending order
    if order == 'desc':
        if len(ingredients):
            recipes = sorted(call_object.get_recipes_by_ingredients(ingredients), key=lambda r: r.name)
        else:
            recipes = call_object.get_all_recipes().order_by('name')
        recipes = [recipe for recipe in reversed(recipes) if query in recipe.name]
    # Filter recipes by query in ascending order
    else:
        if len(ingredients):
            recipes = sorted(call_object.get_recipes_by_ingredients(ingredients), key=lambda r: r.name)
        else:
            recipes = call_object.get_all_recipes().order_by('name')
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
        profile = None
        if request.user.is_authenticated:
            profile = UserProfile.get_or_create_profile(request.user)

        filterRes = _filterRecipes(
            [],
            "",
            request.GET.get('limit'),
            request.GET.get('order'),
            request.GET.get('page'),
            profile,
        )
            
        favorites = None
        if profile:
            favorites = profile.get_favorites()

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
        for maderecipe in profile.get_all_recipes():
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


def deleteRecipe(request):

    user = request.user

    if user.is_authenticated():
        recipe = request.GET['recipe_name']
        profile = UserProfile.get_or_create_profile(user)
        try:
            recipe_id = profile.created_recipes.get(name = recipe).id
        except ObjectDoesNotExist:
            render(request,"user/profile",{'error_message':'This recipe does not exist'})
            return redirect('user.profile')


        profile.delete_recipe(recipe_id)


    return HttpResponse('success')

class editRecipe(View):
    def get (self ,request):
        user  = request.user


        if request.user.is_authenticated():
            recipe_name = request.GET.get('recipe_name')

            profile = UserProfile.get_or_create_profile(user)
            try:
                recipe = profile.created_recipes.get(name = recipe_name)
                recipe_id = recipe.id
            except ObjectDoesNotExist:
                context =  {'error_message':'The recipe with name %s does not exist'%recipe_name}
                return render(request,'recipes/edit.html',context)

            result = 1
            f = RecipeForm(instance = recipe)

            def getfields_name(form):
                i = 0
                k = -1
                ingredient_fields = []
                instructions = []
                for key in form.data.keys():
                    if not key.startswith('in'):
                        continue;
                    if key.startswith('instr'):
                        instructions.append(
                            {'field':'instructions_blob_%i'%i,
                            'value': form.data['instructions_blob_%i'%i]}
                        )
                        i+=1
                    elif key.startswith('ingr'):
                        k+=1

                        ingredient_fields.append(
                            (
                                {'field':'category%s'%k, 'value': form.data['category%s'%k] },
                                {'field':'ingredient%s'%k , 'value':form.data['ingredient%s'%k] },
                                {'field':'quantity%s'%k,  'value':form.data['quantity%s'%k]},
                                {'field':'uom%s'%k ,       'value': form.data['uom%s'%k]}
                            )
                        )

                return (ingredient_fields,instructions)
            fields_name = getfields_name(f)

            context = {
                'recipeform' : f,
                'ingredients_fields':fields_name[0]  ,        #names of ingredient fields
                'instructions': fields_name[1],
                'ingredient_choices':Ingredient.get_all_ingredients(),
                'uom_lookup':Ingredient.get_uom_lookup(),
                'exist':result
            }
            return render(request, "recipes/edit.html",context)
        return redirect(reverse('recipes.search'))


    def post(self,request):
        user = request.user
        result = 0
        if user.is_authenticated():
            recipe_name = request.POST.get('recipe_name')
            data = request.POST.copy()
            data.pop('recipe_name')
            data.update({'name':recipe_name})
            profile = UserProfile.get_or_create_profile(user)

            context = {}
            f = 0
            try:

                recipe = profile.created_recipes.get(name = recipe_name)
                instr_threshold = len(recipe.get_instructions())
                ingr_threshold = recipe.ingredients.count()
                extraStep,extraIQ = self.getExtra(instr_threshold,ingr_threshold,data)
                recipe_id = recipe.id
                f  = RecipeForm(data = data, instance = recipe, extraStep= extraStep,extraIQ=extraIQ)
                if f.is_valid():
                    f.save()
                    result = 1
                    messages.add_message(request, messages.INFO, '%s has been successfully edited'%recipe_name)

                    return redirect('user.profile')
            except ObjectDoesNotExist:

                return render(request,"recipes/edit.html",{'result':result,'error_message':'The recipe with name %s does not exist'%recipe_name})

        context ={'recipeform':f}
        context.update({'error_message': 'Try again, please' })

        return render(request,"recipes/edit.html",context)

    def getExtra(self,instr_threshold,ingr_threshold,data):
        extraIQ,extraStep = [],[]
        for i in range(instr_threshold,instr_threshold+15):
            try:
                extraStep = [data['instructions_blob_%s'%i]]
            except KeyError:
                break
        for i in range(ingr_threshold,ingr_threshold+15):
            try:
                extraIQ = [(data['ingredient%s'%i],data['quantity%s'%i],data['uom%s'%i],data['category%s'%i])]
            except KeyError:
                break

        return extraStep,extraIQ