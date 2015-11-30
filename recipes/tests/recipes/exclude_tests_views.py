from django.test import TransactionTestCase,Client
from user import forms
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from recipes.models import Recipe
from user.models import UserProfile
from ingredients.models import Ingredient
from django.forms.models import model_to_dict
from django.core.exceptions import ObjectDoesNotExist


class RecipeEditTest(TransactionTestCase):

    fixtures = ["recipes.json"]

    def setUp(self):
        self.c = Client()
        user = UserProfile.objects.get(pk=1)
        self.c.login(username ='testcase', password='test')
        self.recipe = Recipe.objects.get(name='mojito')
        self.dic_rec = {
                        "recipe_name": "mojito",                   ## Mojito

                            "ingredient0":"white rum","quantity0":"1.5","category0":"alcohol","uom0":"oz",
                            "ingredient1":"mint","quantity1":"6.0","category1":"produce","uom1":"leaves",
                            "ingredient2":"lime juice","quantity2":"0.5","category2":"juice","uom2":"oz",
                            "ingredient3":"simple syrup","quantity3":"0.5","category3":"syrup","uom3":"oz",
                            "ingredient4":"club soda","quantity4":"1","category4":"soft drink","uom4":"oz",
                            "ingredient5":"lime","quantity5":"1","category5":"produce","uom5":"wedge(s)"
                        ,

                            "instructions_blob_0":"Place mint leaves in the bottom of the glass, add white rum, lime juice, and simple syrup.",
                            "instructions_blob_1":"Muddle all ingredients.",
                            "instructions_blob_2":"Add ice and top with club soda.",
                            "instructions_blob_3":"Garnish with a lime wedge."

                    }
        self.ingr = Ingredient.objects.all()
        self.initial_ing_ct = 6        ## how many ingrendients initially

        # user.created_recipes.add(recipe)

        self.GETresponse = self.c.get('/edit/{}'.format(self.recipe.id))

    def test_GET(self):
        data = self.GETresponse.context
        form = data['form']
        name_of_rec = form.data['name']
        self.assertEqual(name_of_rec,'mojito')

        dic = self.dic_rec

        for i in range(6):
            self.assertTrue(form.data['category%s'%i] in dic.values())
            self.assertTrue(form.data['ingredient%s'%i] in dic.values())



        for i in range(4):
            form_instruction = form.data['instructions_blob_%s'%i]
            instruction = dic['instructions_blob_%s'%i]

            self.assertEqual(form_instruction,instruction)


    def test_ingredients_edits(self):
        data = self.GETresponse.context
        form = data['form']
        name_of_rec = form.data['name']
        self.assertEqual(name_of_rec,'mojito')

        dic = self.dic_rec

        ingredient_removed = dic.pop('ingredient0')                                  #remove ingredient0 (not qty or others)
        ingredient_removed_2 = dic.pop('ingredient5')

        for ing in self.ingr:
            ingredient_added = ing if ing.name != ingredient_removed and ing.name != ingredient_removed_2 else{}

        dic.update({'ingredient0':ingredient_added.name})                                   #update ingredient 0 with a new one

        response = self.c.post('/edit/', dic)                                               #POST it

        self.assertFalse(response.context['recipeform'].is_valid())                         #Should be invalid bc ingredient5 is missing
        self.assertFormError(response,'recipeform',"ingredient5","This field is required.")

        quantity_removed = dic.pop('quantity5')                                          # remove all fields5
        uom_removed = dic.pop('uom5')
        category_removed = dic.pop('category5')

        uom_added = ingredient_added.uom                                                  # Corrects the form by submiiting the right info for new ingredient added
        qty_added = '5.0'
        category_added = ingredient_added.category
        dic.update({'category0':category_added,"uom0":uom_added,"quantity0":qty_added})

        response = self.c.post('/edit/', dic)

        #self.assertTrue(response.context. .is_valid())

        new_recipe = Recipe.objects.get(name = name_of_rec)                  #this is the new recipe once its been edited (one less ingredient:ingredient5)

        self.assertNotEqual(new_recipe.ingredients.all().count(), self.initial_ing_ct,"Error: Counts match")

        ingredient_removed = Ingredient.objects.get(name = ingredient_removed)
        with self.assertRaises(ObjectDoesNotExist):
            new_recipe.ingredients.get(name = ingredient_removed)                 # asssert the ingredient isnt there anymore


        def test_instructions_edit(self):
            data = self.GETresponse.context                         #Initialization get the form
            form = data['form']
            name_of_rec = form.data['name']
            self.assertEqual(name_of_rec,'mojito')                  #Verify we got the right one


            dic = self.dic_rec

            instruction_removed = dic.pop('instructions_blob_3')

            response = self.c.post('/edit/', dic)

            self.assertTrue("mojito has been successfully edited" in response.context['messages'])            #No form is returned when succeeds


        def extra_ingredients(self):
            data = self.GETresponse.context                         #Initialization get the form
            form = data['form']
            name_of_rec = form.data['name']
            self.assertEqual(name_of_rec,'mojito')                  #Verify we got the right one

            dic = self.dic_rec

            dic.update({
                'ingredient6':'water' , 'category6':'liquid', 'uom6':'liters','quantity6':'6.0'   #One more and new ingredient
            })

            response = self.post('/edit/', dic)

            self.assertEqual(Ingredient.objects.get(name = 'water').name, "water")

            new_recipe = Recipe.objects.get(name = name_of_rec)

            self.assertEqual(new_recipe.ingredients.get(name = 'water').name, 'water')

            self.assertNotEqual(new_recipe.ingredients.all().count(), self.initial_ing_ct,"Error: Counts match")


        def extra_instructions(self):
            data = self.GETresponse.context                         #Initialization get the form
            form = data['form']
            name_of_rec = form.data['name']
            self.assertEqual(name_of_rec,'mojito')                  #Verify we got the right one

            dic = self.dic_rec

            dic.update({
                'instructions_blob_4': 'One more instruction to test'   #One more instruction
            })

            response = self.post('/edit/', dic)

            new_recipe = Recipe.objects.get(name = name_of_rec)

            self.assertTrue('One more instruction to test' in new_recipe.instructions_blob)








