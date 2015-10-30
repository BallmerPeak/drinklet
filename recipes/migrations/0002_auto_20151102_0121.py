# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ingredients', '0001_initial'),
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='recipe',
            old_name='instructions',
            new_name='instructions_blob',
        ),
        migrations.AddField(
            model_name='recipe',
            name='ingredients',
            field=models.ManyToManyField(related_name='recipe_ingredients', through='recipes.RecipeIngredients', to='ingredients.Ingredient'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='name',
            field=models.CharField(max_length=30, unique=True),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='ratings_sum',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='total_ratings',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
