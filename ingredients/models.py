from django.db import models

# Create your models here.


class Ingredient(models.Model):
    name = models.CharField(max_length=30)
    category = models.CharField(max_length=30)
    uom = models.CharField(max_length=10)

    @classmethod
    def get_all_ingredients(cls):
        return list(cls.objects.all())
