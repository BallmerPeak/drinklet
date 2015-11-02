from django.db import models

# Create your models here.


class Ingredient(models.Model):
    name = models.CharField(max_length=30)
    category = models.CharField(max_length=30)
    uom = models.CharField(max_length=10)

    def __str__(self):
        return self.name

    @classmethod
    def get_all_ingredients(cls):
        ret_dict = {}
        ingredients = cls.objects.all()
        categories = ingredients.values_list('category', flat=True).distinct()
        for category in categories:
            ret_dict[category] = ingredients.filter(category=category)

        return ret_dict
