## Run `python manage.py runscript seed_recipes`

from django.db import IntegrityError

from recipes.models import Recipe, RecipeIngredients
from ingredients.models import Ingredient

all_ingredients = Ingredient.objects.all()

def get_ingredient(_name):
	ingredient_object = list(all_ingredients.filter(name=_name)[:1])
	if ingredient_object:
		return ingredient_object[0]
	return None

recipe_array = [
	## Gin & Tonic
	{
		"name":"gin & tonic",
		"ingredients": {
			"gin":"1.25",
			"tonic":"3",
			"lime":"1"
		},
		"instructions": [
			"Fill a highball glass with ice.",
			"Place a lime wheel on top of the ice.",
			"Pour Gin over the ice and add tonic water."
		]
	},

	## Margarita
	{
		"name": "margarita",
		"ingredients": {
			"tequila":"1",
			"orange liqueur":"0.5",
			"lime juice":"2",
			"crushed ice":"4",
			"lime":"1",
			"salt":"1"
		},
		"instructions": [
			"Rub rim of a chilled rocks glass with lime.",
			"Dip glass into salt to coat.",
			"Fill shaker with ice.",
			"Add orange liqeuer, tequila, and lime juice.",
			"Shake well.",
			"Strain drink into the rocks glass filled with ice.",
			"Garnish with lime wedge."
		]
	},

	## Mojito
	{
		"name": "mojito",
		"ingredients": {
			"white rum":"1.5",
			"mint":"6",
			"lime juice":"0.5",
			"simple syrup":"0.5",
			"club soda":"1",
			"lime":"1"
		},
		"instructions": [
			"Place mint leaves in the bottom of the glass, add white rum, lime juice, and simple syrup.",
			"Muddle all ingredients.",
			"Add ice and top with club soda.",
			"Garnish with a lime wedge."
		]
	}
]

for recipe in recipe_array:
	r = Recipe(name=recipe.get("name"), instructions_blob=('~~~'.join(recipe.get("instructions"))))
	try:
		r.save()
	except IntegrityError as e:
		print(recipe.get("name") + " is already in the database.")
		continue

	for _ingredient, _quantity in recipe.get("ingredients").iteritems():
		i = RecipeIngredients(recipe=r, ingredient=get_ingredient(_ingredient), quantity=_quantity)
		try:
			i.save()
		except IntegrityError as e:
			print(_ingredient + " is already connected to a " + recipe.get("name") + " recipe.")
			continue

print("** Recipes Seeded **")


