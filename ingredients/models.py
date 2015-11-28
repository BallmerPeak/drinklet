from django.db import models

# Create your models here.


class Ingredient(models.Model):
    name = models.CharField(max_length=30, unique=True)
    category = models.CharField(max_length=30)
    uom = models.CharField(max_length=10)

    def __str__(self):
        return self.name

    @classmethod
    def get_all_ingredients(cls):
        ret_dict = {}
        ingredients = cls.objects.all().only('name')
        categories = ingredients.values_list('category', flat=True).distinct()
        for category in categories:
            ret_dict[category] = ingredients.filter(category=category)

        return ret_dict

    @classmethod
    def get_uom_lookup(cls):
        return {
            ingredient.name: ingredient.uom
            for ingredient in
            cls.objects.all().defer('category')
            }

    @classmethod
    def _create_ingredient_objs(cls, ingredients):

        ingredient_objs = []

        for name, category, quantity, uom in ingredients:
            ingredient = cls(name=name, category=category, uom=uom)
            ingredient.save()
            ingredient_objs.append((ingredient.id, quantity))

        return ingredient_objs
