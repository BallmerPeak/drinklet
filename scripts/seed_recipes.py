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
			"lime":"1",
			"salt":"1"
		},
		"instructions": [
			"Rub rim of a chilled rocks glass with lime.",
			"Dip glass into salt to coat.",
			"Fill shaker with ice.",
			"Add orange liqueur, tequila, and lime juice.",
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
	},

	## White Russian
	{
		"name": "white russian",
		"ingredients": {
			"coffee liqueur":"0.66",
			"vodka":"1.66",
			"fresh cream":"1"
		},
		"instructions": [
			"Pour coffee liqueur and vodka into an Old Fashioned glass filled with ice.",
			"Float fresh cream on top and stir slowly."
		]
	},

	## Mud Slide
	{
		"name": "mud slide",
		"ingredients": {
			"coffee liqueur":"1",
			"vodka":"1",
			"cream liqueur":"1",
			"fresh cream":"1"
		},
		"instructions": [
			"Add all the ingredients to a blender and blend until smooth.",
			"Pour the Mudslide into a Martini or Hurricane glass.",
			"If desired, drizzle with chocolate syrup."
		]
	},

	## Bahama Mama
	{
		"name": "bahama mama",
		"ingredients": {
			"rum":"0.5",
			"coconut rum":"0.5",
			"grenadine syrup":"0.5",
			"orange juice":"1",
			"pineapple juice":"1"
		},
		"instructions": [
			"Combine regular rum, rum with coconut flavoring, grenadine, orange juice, pineapple juice and crushed ice in an electric blender.",
			"Blend until the drink's consistency is slushy."
		]
	},

	## Cosmopolitan
	{
		"name": "Cosmopolitan",
		"ingredients": {
			"lime juice":"0.5",
			"cranberry juice":"1", 
			"orange liqueur":"0.5",
			"vodka":"1.5"
		},
		"instructions": [
			"Add all ingredients into cocktail shaker filled with ice.",
			"Shake well and double strain into large cocktail glass.",
			"Garnish with lime wheel."
		]
	},

	## Screwdriver
	{
		"name": "screwdriver",
		"ingredients": {
			"vodka":"1.75",
			"orange juice":"3.5"
		},
		"instructions": [
			"Mix in a highball glass with ice.",
			"Garnish and serve."
		]
	},

	# Martini
	{
		"name": "Martini",
		"ingredients": {
			"dry vermouth":"0.5",
			"gin":"3"
		},
		"instructions": [
			"Pour all ingredients into mixing glass with ice cubes.",
			"Stir well.",
			"Strain in chilled martini cocktail glass.",
			"Squeeze oil from lemon peel onto the drink or garnish with olive."
		]
	},

	# Daiquiri
	{
		"name": "daiquiri",
		"ingredients": {
			"white rum":"1.5",
			"simple syrup":"0.5",
			"lime juice":"1"
		},
		"instructions": [
			"Pour all ingredients into shaker with ice cubes.",
			"Shake well.",
			"Strain in chilled cocktail glass."
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

	for _ingredient, _quantity in recipe.get("ingredients").items():
		i = RecipeIngredients(recipe=r, ingredient=get_ingredient(_ingredient), quantity=_quantity)
		try:
			i.save()
		except IntegrityError as e:
			print(_ingredient + " is already connected to a " + recipe.get("name") + " recipe.")
			continue

print("** Recipes Seeded **")


