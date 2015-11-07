## Run `python manage.py runscript seed_ingredients`

from django.db import IntegrityError

from ingredients.models import Ingredient

ingredient_array = [
	# Alcohol
	["gin", "alcohol", "oz"],
	["tequila", "alcohol", "oz"],
	["orange liqueur", "alcohol", "oz"],
	["white rum", "alcohol", "oz"],

	# Soft Drink
	["tonic", "soft drink", "oz"],
	["club soda", "soft drink", "oz"],
	# Juice

	["lime juice", "juice", "oz"],

	# Produce
	["lime", "produce", "wedge(s)"],
	["mint", "produce", "leaves"],

	# Misc
	["crushed ice", "misc", "oz"],
	["ice cube", "misc", "cube(s)"],
	["salt", "misc", "pinch(es)"],
	["simple syrup", "misc", "oz"],

]

for ingredient in ingredient_array:
	i = Ingredient(name=ingredient[0], category=ingredient[1], uom=ingredient[2])
	try:
		i.save()
	except IntegrityError as e:
		print(ingredient[0] + " is already in the database.")

print("** Ingredients Seeded **")