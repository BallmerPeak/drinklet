from django import forms

from ingredients.models import Ingredient
from decimal import Decimal

CATEGORY_NAME = 'added_category_'
INGREDIENT_NAME = 'added_ingredient_'
INSTRUCTION_NAME = 'added_instruction_'
QTY_NAME = 'added_qty_'
UOM_NAME = 'added_uom_'
CATEGORY_INDEX = len(CATEGORY_NAME)
INGREDIENT_ID_INDEX = len(INGREDIENT_NAME)
INSTRUCTION_ID_INDEX = len(INSTRUCTION_NAME)
QTY_INDEX = len(QTY_NAME)
UOM_INDEX = len(UOM_NAME)


class RecipeForm(forms.Form):
    recipe_name = forms.CharField(max_length=30)
    ingredient = forms.CharField(max_length=30)
    ingredient_qty = forms.DecimalField(decimal_places=2)
    instruction = forms.CharField(max_length=100)
    uom = forms.CharField(max_length=10)
    ingr_index = 1
    inst_index = 1

    def __init__(self, *args, **kwargs):
        super(RecipeForm, self).__init__(*args, **kwargs)
        self.ingredient_choices = Ingredient.get_all_ingredients()
        self.categories = forms.ChoiceField(choices=self._get_category_choices())

        instruction_list = []
        qty_list = []
        ingredient_list = []
        category_list = []
        uom_list = []

        if args[0]:
            for name, _ in args[0].items():
                if name.startswith(INSTRUCTION_NAME):
                    instruction_list.append(name)
                elif name.startswith(QTY_NAME):
                    qty_list.append(name)
                elif name.startswith(INGREDIENT_NAME):
                    ingredient_list.append(name)
                elif name.startswith(CATEGORY_NAME):
                    category_list.append(name)
                elif name.startswith(UOM_NAME):
                    uom_list.append(name)

            instruction_list.sort(key=lambda inst_key: int(inst_key[INSTRUCTION_ID_INDEX:]))
            qty_list.sort(key=lambda qty_key: int(qty_key[QTY_INDEX:]))
            ingredient_list.sort(key=lambda ingr_key: int(ingr_key[INGREDIENT_ID_INDEX:]))
            category_list.sort(key=lambda cat_key: int(cat_key[CATEGORY_INDEX:]))
            uom_list.sort(key=lambda uom_key: int(uom_key[UOM_INDEX:]))
            self.inst_index = len(instruction_list) + 1
            self.ingr_index = len(ingredient_list) + 1

            for key in instruction_list:
                self.fields[key] = forms.CharField(max_length=100)

            for key in qty_list:
                self.fields[key] = forms.DecimalField(decimal_places=2)

            for key in ingredient_list:
                self.fields[key] = forms.CharField(max_length=30)

            for key in category_list:
                self.fields[key] = forms.ChoiceField(choices=self._get_category_choices())

            for key in uom_list:
                self.fields[key] = forms.CharField(max_length=10)

    def clean(self):
        cleaned_data = super(RecipeForm, self).clean()

        for name, value in self.data.items():
            if name.startswith(INGREDIENT_NAME):
                i = int(name[INGREDIENT_ID_INDEX:])
                qty = Decimal(self.data['{}{}'.format(QTY_NAME, i)])
                try:
                    cleaned_data[name] = {
                        Ingredient.objects.only('id').get(name=value.lower()).id:
                        qty
                    }
                except Ingredient.DoesNotExist:
                    category = self.data["{}{}".format(CATEGORY_NAME, i)]
                    uom = self.data['{}{}'.format(UOM_NAME, i)]
                    cleaned_data[name] = {
                        value.lower(): (category, qty, uom)
                    }
        return cleaned_data

    def clean_ingredient(self):
        qty = Decimal(self.data['ingredient_qty'])
        ingredient_data = (self.data['ingredient']).lower()
        try:
            ingredient_data = {
                Ingredient.objects.only('id').get(name=ingredient_data).id: qty
            }
        except Ingredient.DoesNotExist:
            category = self.data['categories']
            uom = self.data['uom']
            ingredient_data = {
                ingredient_data: (category, qty, uom)
            }

        return ingredient_data

    def clean_recipe_name(self):
        return self.data['recipe_name'].lower()

    def get_name(self):
        try:
            return self.cleaned_data['recipe_name']
        except (KeyError, AttributeError):
            try:
                return self.data['recipe_name']
            except KeyError:
                return ''

    def get_instruction(self):
        try:
            return self.cleaned_data['instruction']
        except (KeyError, AttributeError):
            try:
                return self.data['instruction']
            except KeyError:
                return ''

    def _get_category_choices(self):
        return [
            (category, category) for category, _ in self.ingredient_choices.items()
        ]

    def get_ingredient_choices(self):
        return [
            (ingredient.id, ingredient.name)
            for _, ingredients in self.ingredient_choices.items()
            for ingredient in ingredients
        ]

    # ############### Field accessor methods ##############################
    # #####################################################################
    def get_instruction_fields(self):
        instructions = [{
            'field_name': 'instruction',
            'instruction': self.data.get('instruction', '')
        }]
        added_instructions = []
        for name, value in self._get_data_generator(INSTRUCTION_NAME):
            added_instructions.append({
                'field_name': name,
                'instruction': value
            })
        added_instructions.sort(key=lambda instruction: int(instruction['field_name'][INSTRUCTION_ID_INDEX:]))
        return instructions + added_instructions

    def get_qty_fields(self):
        qtys = [{
            'field_name': 'ingredient_qty',
            'qty': self.data.get('ingredient_qty', '')
        }]
        added_qty = []
        for name, value in self._get_data_generator(QTY_NAME):
            added_qty.append({
                'field_name': name,
                'qty': value
            })
        added_qty.sort(key=lambda qty: int(qty['field_name'][QTY_INDEX:]))
        return qtys + added_qty

    def get_ingredient_fields(self):
        ingredients = [{
            'field_name': 'ingredient',
            'ingredient': self.data.get('ingredient', '')
        }]
        added_ingredients = []
        for name, value in self._get_data_generator(INGREDIENT_NAME):
            added_ingredients.append({
                'field_name': name,
                'ingredient': value
            })
        added_ingredients.sort(key=lambda ingredient: int(ingredient['field_name'][INGREDIENT_ID_INDEX:]))
        return ingredients + added_ingredients

    def get_category_fields(self):
        categories = [{
            'field_name': 'categories',
            'category': self.data.get('categories', '')
        }]
        added_categories = []
        for name, value in self._get_data_generator(CATEGORY_NAME):
            added_categories.append({
                'field_name': name,
                'category': value
            })
        added_categories.sort(key=lambda category: int(category['field_name'][CATEGORY_INDEX:]))
        return categories + added_categories

    def get_uom_fields(self):
        uoms = [{
            'field_name': 'uom',
            'uom': self.data.get('uom', '')
        }]
        added_uom = []
        for name, value in self._get_data_generator(UOM_NAME):
            added_uom.append({
                'field_name': name,
                'uom': value
            })
        added_uom.sort(key=lambda uom: int(uom['field_name'][UOM_INDEX:]))
        return uoms + added_uom

    # ########### Cleaned Data accessor methods ###########################
    # #####################################################################

    def get_clean_ingredients(self):
        ingredients = {}
        ingredients.update(self.cleaned_data['ingredient'])

        for _, ingredient in self._get_clean_data_generator(INGREDIENT_NAME):
            ingredients.update(ingredient)

        return ingredients

    def get_clean_instructions(self):
        instructions = [self.cleaned_data['instruction']]

        ordered_instructions = sorted([(name, instruction) for name, instruction
                                       in self._get_clean_data_generator(INSTRUCTION_NAME)],
                                      key=lambda x: int(x[0][INSTRUCTION_ID_INDEX:]))

        return instructions + [instruction for _, instruction in ordered_instructions]

    # ########### Helper Methods ##########################################
    # #####################################################################

    def _get_data_generator(self, name_startswith):
        for name, value in self.data.items():
            if name.startswith(name_startswith):
                yield (name, value)

    def _get_clean_data_generator(self, name_startswith):
        for name, value in self.cleaned_data.items():
            if name.startswith(name_startswith):
                yield (name, value)

    # ########### Field Name Accessor Methods #############################
    # #####################################################################

    @classmethod
    def get_ingredient_name(cls):
        return INGREDIENT_NAME

    @classmethod
    def get_qty_name(cls):
        return QTY_NAME

    @classmethod
    def get_instruction_name(cls):
        return INSTRUCTION_NAME

    @classmethod
    def get_category_name(cls):
        return CATEGORY_NAME

    @classmethod
    def get_uom_name(cls):
        return UOM_NAME
