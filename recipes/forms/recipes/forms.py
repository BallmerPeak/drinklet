from django.forms import ModelForm,fields ,widgets,TextInput
from django.forms.models import model_to_dict, fields_for_model,ModelChoiceField
from django.forms import CharField


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



class RecipeForm(ModelForm):

        def __init__(self,data = None ,instance = None, *args,**kwargs):
            i = 0
            _fields = ('ingredient0', 'quantity0')
            _initial = {}
            ###extraIQ is a list of tuples(ingredient,quantity)
            extraIQ = kwargs.pop('extraIQ',[])

            extraStep = kwargs.pop('extraStep',[])
            var2 = len(extraStep)



            var = []
            var3 = 1
            if data is None :
                if instance is not None and isinstance(instance,Recipe):
                    var = instance.recipeingredients_set.all()
                    steps = instance.instructions_blob.split('~~~')
                    var3 = len(steps)
                    data = {'name':instance.name}
                    for k,step in enumerate(steps,0):
                        data.update({'instructions_blob_%d'%k: step})





            ##For ingregredients and quanttities fields for viewing recipes
                for i, field in enumerate(var,i):
                    # dict = model_to_dict(field, ('ingredient', 'quantity',))
                    #_initial.update({'ingredient%d'%i : field.ingredient.name, 'quantity%d'%i : field.quantity})
                    _fields = _fields + ('ingredient%d'%i, 'quantity%d'%i)
                    data.update({'ingredient%d'%i : field.ingredient.name, 'quantity%d'%i : field.quantity})
                    #initial = _initial

            for i,field in enumerate(extraIQ,i or 1):
                #_initial.update({'ingredient%d'%i : field[0], 'quantity%d'%i : field[1]})
                _fields = _fields + ('ingredient%d'%i, 'quantity%d'%i)
                data.update({'ingredient%d'%i : field[0], 'quantity%d'%i : field[1]})
                #initial = _initial



            # Pass the initial data to the base
            super(RecipeForm, self).__init__(data = data or None, instance=instance, *args, **kwargs)


            # Retrieve the fields from the recipe_ingredients model and update the fields with it
            #self.fields.update(fields_for_model(Recipe,('name','instructions_blob')))
            b = fields_for_model(RecipeIngredients, ('ingredient','quantity'))
            for j in range(i+1) :

                #value =  Ingredient.objects.get(name =_initial['ingredient%d'%j])
                b["ingredient"] =  ModelChoiceField(queryset = Ingredient.objects.all(), empty_label = None,to_field_name = 'name', required = True )
                self.fields.update({'ingredient%d'%j:b["ingredient"] , 'quantity%d'%j:b["quantity"]})


        ##For instructions fields

                #var2 = var + var2

                # n = 0
                # for i in range(var,var2):
                #     self.fields['instructions_blob'].fields[i] = extraStep[n]
                #     n+=1
            #self.fields['instructions_blob'].widget.value_from_datadict(data = data,files = None ,name = 'widget')
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

            for i, field in enumerate(u,0):
                field.ingredient = self.cleaned_data['ingredient%d'%i]
                field.quantity = self.cleaned_data['quantity%d'%i]
                field.save()

            u = self.instance
            u.name = self.cleaned_data['name']
            u.instructions_blob = self.cleaned_data['instructions_blob']
            u.save()

            recipe = super(RecipeForm, self).save(*args,**kwargs)
            return recipe




import django
django.setup()
rec = Recipe.objects.get(name ='margarita')
f = RecipeForm(instance = rec)
print(f)
f.is_valid()
print(f.is_valid())
print("~~~~~~\n")
print(f.cleaned_data)
f = RecipeForm(data = {},instance = rec,extraStep= ['NEW STEP TEST','JUST A TEST'])
print("~~~~~~\n")
print(f.is_valid())
print("~~~~~~\n")
print(f.errors)
print(f)
#f.save()




