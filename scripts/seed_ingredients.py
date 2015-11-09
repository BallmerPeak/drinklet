## Run `python manage.py runscript seed_ingredients`

from django.db import IntegrityError
from ingredients.models import Ingredient

ingredient_array = [
    # Alcohol
    ("gin", "alcohol", "oz"),
    ("tequila", "alcohol", "oz"),
    ("orange liqueur", "alcohol", "oz"),
    ("white rum", "alcohol", "oz"),
    ("coffee liqueur", "alcohol", "oz"),
    ("vodka", "alcohol", "oz"),
    ("cream liqueur", "alcohol", "oz"),
    ("rum", "alcohol", "oz"),
    ("coconut rum", "alcohol", "oz"),
    ("dry vermouth", "alcohol", "oz"),

    # Soft Drink
    ("tonic", "soft drink", "oz"),
    ("club soda", "soft drink", "oz"),

    # Juice
    ("lime juice", "juice", "oz"),
    ("orange juice", "juice", "oz"),
    ("pineapple juice", "juice", "oz"),
    ("cranberry juice", "juice", "oz"),

    # Produce
    ("lime", "produce", "wedge(s)"),
    ("mint", "produce", "leaves"),

    # Syrup
    ("simple syrup", "syrup", "oz"),
    ("grenadine syrup", "syrup", "oz"),

    # Misc
    ("salt", "misc", "pinch(es)"),
    ("fresh cream", "misc", "oz"),
]

for ingredient, category, uom in ingredient_array:
    i = Ingredient(name=ingredient, category=category, uom=uom)
    try:
        i.save()
    except IntegrityError as e:
        print(ingredient + " is already in the database.")

print("** Ingredients Seeded **")
