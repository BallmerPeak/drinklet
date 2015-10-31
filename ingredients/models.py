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
        return cls.objects.all()
