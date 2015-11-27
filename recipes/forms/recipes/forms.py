from django.forms import ModelForm,fields ,widgets,TextInput
from django.forms.models import model_to_dict, fields_for_model,ModelChoiceField
from django.forms import CharField
from recipes.models import Recipe

from recipes.models import Recipe,RecipeIngredients,Ingredient



class MyWidget(widgets.MultiWidget):

    def __init__(self, attrs=None,**kwargs):

        w_needed = kwargs.pop('w_needed',0)

        _widgets = [TextInput()]
        _widgets *= w_needed
        super(MyWidget, self).__init__(_widgets, attrs)

    def decompress(self, value):
        if value:
            return value.split('~~~')
        else:
            return []

class MyInstructionField(fields.MultiValueField):

    widget = MyWidget
    def __init__(self,*args,**kwargs):
        f_needed = kwargs.pop('f_needed',0)
        var = kwargs.pop('extraStep',0)
        kwargs.pop('f_needed',0)
        if var:
            f_needed += var


        _fields = [fields.CharField(max_length=1000)] * f_needed

        self.widget = MyWidget(w_needed= f_needed)
        #del kwargs['f_needed']
        super(MyInstructionField, self).__init__(_fields,require_all_fields=True, *args, **kwargs)

    def compress(self, data_list):
        intr_blob = ''
        if data_list:
            instr_blob = "~~~".join(data_list)

        return instr_blob

class MyChoiceField(ModelChoiceField):

    def validate(self,value):
        return



class RecipeForm(ModelForm):

        def __init__(self,data = None ,instance = None, *args,**kwargs):
            i = 1
            _fields = ('ingredient0', 'quantity0','uom0','category0')
            _initial = {}
            ###extraIQ is a list of 4-tuples(ingredient,quantity,uom,cat)
            extraIQ = kwargs.pop('extraIQ',[])

            extraStep = kwargs.pop('extraStep',[])
            var2 = len(extraStep)


            self.inst_index = 1
            self.ingr_index = 1
            var = []
            var = instance.recipeingredients_set.all()
            if data is not None:
                if extraIQ:
                    i = len(var)
                else :
                    i = self.findcountofing(data)         ##new count of ingredients fields less than instance

            steps = instance.instructions_blob.split('~~~')
            var3 = len(steps)
            if data is None :
                if instance is not None and isinstance(instance,Recipe):

                    data = {'name':instance.name}
                    for k,step in enumerate(steps,0):
                        data.update({'instructions_blob_%d'%k: step})
                        self.inst_index += 1




            ##For ingregredients and quanttities fields for viewing recipes
                for i, field in enumerate(var,0):
                    #dict = model_to_dict(field, ('ingredient', 'quantity',))
                    #_initial.update({'ingredient%d'%i : field.ingredient.name, 'quantity%d'%i : field.quantity})
                    _fields = _fields + ('ingredient%d'%i, 'quantity%d'%i,'uom%d'%i)
                    data.update({'ingredient%d'%i : field.ingredient.name,
                                 'quantity%d'%i : field.quantity,
                                 'uom%d'%i:field.ingredient.uom,
                                 'category%d'%i:field.ingredient.category})
                    self.ingr_index+=1
                    #initial = _initial

            for i,field in enumerate(extraIQ,i or 1):
                #_initial.update({'ingredient%d'%i : field[0], 'quantity%d'%i : field[1]})
                _fields = _fields + ('ingredient%d'%i, 'quantity%d'%i,'uom%d'%i,'category%d'%i)
                data.update({'ingredient%d'%i : field[0],
                             'quantity%d'%i : field[1],
                             'uom%d'%i:field[2],
                             'category%d'%i:field[3]})




            # Pass the initial data to the base
            super(RecipeForm, self).__init__(data = data or None, instance=instance, *args, **kwargs)


            # Retrieve the fields from the recipe_ingredients model and update the fields with it
            #self.fields.update(fields_for_model(Recipe,('name','instructions_blob')))
            b = fields_for_model(RecipeIngredients, ('ingredient','quantity'))
            uomFormField = fields_for_model(Ingredient,['uom'])
            categoryFormField = fields_for_model(Ingredient,['category'])
            for j in range(i) :


                #value =  Ingredient.objects.get(name =_initial['ingredient%d'%j])
                b["ingredient"] =  ModelChoiceField(queryset = Ingredient.objects.all(), empty_label = None,to_field_name = 'name', required = True )
                self.fields.update({'ingredient%d'%j:b["ingredient"] ,
                                    'quantity%d'%j:b["quantity"],
                                    'uom%d'%j:uomFormField['uom'],
                                    'category%d'%j:categoryFormField['category']})


        ##For instructions fields


            self.fields['instructions_blob'] = MyInstructionField(extraStep=var2, f_needed = var3 )

            if extraStep:
                for k,step in enumerate(extraStep,var3):
                    data.update({'instructions_blob_%d'%k: step})

            #self.full_clean()






        instructions_blob = MyInstructionField()

        class Meta:
            model = Recipe
            fields = ['name']

        def save(self, *args, **kwargs):
            u = self.instance.recipeingredients_set.all()
            count = self.findcountofing(self.cleaned_data)
            ingredients_dic = {}

            for i in range (count):
                n = str(self.cleaned_data['quantity%d'%i])
                if isinstance(self.cleaned_data['ingredient%d'%i],str):
                    ingredients_dic.update({
                        self.cleaned_data['ingredient%d'%i]:(self.cleaned_data['category%d'%i],n,self.cleaned_data['uom%d'%i])
                    })
                else:
                    ingredients_dic.update({
                        self.cleaned_data['ingredient%d'%i].id:n
                    })


            u = self.instance
            name = self.cleaned_data['name']
            instructions_blob = self.cleaned_data['instructions_blob']
            u.edit_recipe(name,instructions_blob,ingredients_dic)

            recipe = super(RecipeForm, self).save(*args,**kwargs)

            return recipe

        def full_clean(self):
            super(RecipeForm, self).full_clean()
            v = []
            for error in self._errors:
                if 'ingredient' in error and 'valid choice' in error:
                    v += [error]
                    self.cleaned_data.update({error:self.data[error]})
            for key in v:
                del self._errors[key]


            return self.cleaned_data

        def findcountofing(self,data):
            max = 0
            for var in data.keys():
                if var.startswith('ingr') or var.startswith('qua') or var.startswith('uom') or var.startswith('cat'):
                    if max < int(var[len(var)-1]):
                        max = int(var[len(var)-1])
            return max+1


@classmethod
def get_ingredient_name(cls):
    return 'ingredient'

@classmethod
def get_qty_name(cls):
    return 'quantity'

@classmethod
def get_instruction_name(cls):
    return 'instructions_blob_'

@classmethod
def get_category_name(cls):
    return 'category'

@classmethod
def get_uom_name(cls):
    return 'uom'



dic_rec = {
                        "name": "mojito",                   ## Mojito

                            "ingredient0":"amadou","quantity0":"1.5","category0":"alcohol","uom0":"oz",
                            "ingredient1":"mint","quantity1":"6.0","category1":"produce","uom1":"leaves",
                            "ingredient2":"lime juice","quantity2":"0.5","category2":"juice","uom2":"oz",
                            "ingredient3":"simple syrup","quantity3":"0.5","category3":"syrup","uom3":"oz"

                        ,

                            "instructions_blob_0":"Place mint leaves in the bottom of the glass, add white rum, lime juice, and simple syrup.",
                            "instructions_blob_1":"Muddle all ingredients.",
                            "instructions_blob_2":"Add ice and top with club soda.",
                            "instructions_blob_3":"Garnish with a lime wedge."

                    }



