## Run `python manage.py runscript seed_recipes`

from django.db import IntegrityError
from recipes.models import Recipe, RecipeIngredients
from ingredients.models import Ingredient
from user.models import UserProfile

all_ingredients = Ingredient.objects.all()


def get_ingredient(_name):
    ingredient_object = list(all_ingredients.filter(name=_name)[:1])
    if ingredient_object:
        return ingredient_object[0]
    return None


recipe_array = [
    # ## Gin & Tonic
    # (
    #     "gin & tonic",
    #     [
    #         "Fill a highball glass with ice.",
    #         "Place a lime wheel on top of the ice.",
    #         "Pour Gin over the ice and add tonic water."
    #     ],
    #     {
    #         1: "1.25",
    #         11: "3",
    #         17: "1"
    #     }
    # ),

    ## Margarita
    (
        "margarita",
		[
            "Rub rim of a chilled rocks glass with lime.",
            "Dip glass into salt to coat.",
            "Fill shaker with ice.",
            "Add orange liqueur, tequila, and lime juice.",
            "Shake well.",
            "Strain drink into the rocks glass filled with ice.",
            "Garnish with lime wedge."
        ],
        {
            2: "1",
            3: "0.5",
            13: "2",
            17: "1",
            21: "1"
        }
    ),

    ## Mojito
    (
        "mojito",
		[
            "Place mint leaves in the bottom of the glass, add white rum, lime juice, and simple syrup.",
            "Muddle all ingredients.",
            "Add ice and top with club soda.",
            "Garnish with a lime wedge."
        ],
        {
            4: "1.5",
            18: "6",
            13: "0.5",
            19: "0.5",
            12: "1",
            17: "1"
        }

    ),

    ## White Russian
    (
        "white russian",
		[
            "Pour coffee liqueur and vodka into an Old Fashioned glass filled with ice.",
            "Float fresh cream on top and stir slowly."
        ],
        {
            5: "0.66",
            6: "1.66",
            22: "1"
        }

    ),

    ## Mud Slide
    (
        "mud slide",
		[
            "Add all the ingredients to a blender and blend until smooth.",
            "Pour the Mudslide into a Martini or Hurricane glass.",
            "If desired, drizzle with chocolate syrup."
        ],
        {
            5: "1",
            6: "1",
            7: "1",
            22: "1"
        }

    ),

    ## Bahama Mama
    (
        "bahama mama",
		[
            "Combine regular rum, rum with coconut flavoring, grenadine, orange juice, pineapple juice and crushed ice in an electric blender.",
            "Blend until the drink's consistency is slushy."
        ],
        {
            8: "0.5",
            9: "0.5",
            20: "0.5",
            14: "1",
            15: "1"
        }

    ),

    ## Cosmopolitan
    (
        "Cosmopolitan",
		[
            "Add all ingredients into cocktail shaker filled with ice.",
            "Shake well and double strain into large cocktail glass.",
            "Garnish with lime wheel."
        ],
        {
            13: "0.5",
            16: "1",
            3: "0.5",
            6: "1.5"
        }

    ),

    ## Screwdriver
    (
        "screwdriver",
		[
            "Mix in a highball glass with ice.",
            "Garnish and serve."
        ],
        {
            6: "1.75",
            14: "3.5"
        }

    ),

    # Martini
    (
        "Martini",
		[
            "Pour all ingredients into mixing glass with ice cubes.",
            "Stir well.",
            "Strain in chilled martini cocktail glass.",
            "Squeeze oil from lemon peel onto the drink or garnish with olive."
        ],
        {
            10: "0.5",
            1: "3"
        },

    ),

    # Daiquiri
    (
        "daiquiri",
		[
            "Pour all ingredients into shaker with ice cubes.",
            "Shake well.",
            "Strain in chilled cocktail glass."
        ],
        {
            4: "1.5",
            19: "0.5",
            13: "1"
        }

    )
]

profile = UserProfile.objects.get(pk=1)
for recipe in recipe_array:
    profile.create_recipe(*recipe)


print("** Recipes Seeded **")
