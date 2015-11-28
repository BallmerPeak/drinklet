class RecipeInfo:
    def __init__(self, recipe, user_ingredients):
        self.recipe = recipe
        self.user_ingredients = user_ingredients
        self.missing_ingredients = []
        self.num_can_make = self._quantity_drinks()

    def _quantity_drinks(self):
        user_ingredients = self._dictify_user_ingredients()
        recipe_ingredients = self.recipe.recipeingredients_set.all()
        num_can_make_list = []

        for recipe_ingredient in recipe_ingredients:
            try:
                user_ingredient = user_ingredients[recipe_ingredient.ingredient]
                multiple_of_ingredients = int(user_ingredient.quantity / recipe_ingredient.quantity)

                if multiple_of_ingredients == 0:
                    self.missing_ingredients.append((recipe_ingredient.ingredient.id,
                                                     recipe_ingredient.quantity - user_ingredient.quantity))
                num_can_make_list.append(multiple_of_ingredients)
            except KeyError:
                self.missing_ingredients.append((recipe_ingredient.ingredient.id, recipe_ingredient.quantity))
                num_can_make_list.append(0)

        return min(num_can_make_list)

    def _dictify_user_ingredients(self):
        return {
            user_ingredient.ingredient: user_ingredient
            for user_ingredient in self.user_ingredients
        }

