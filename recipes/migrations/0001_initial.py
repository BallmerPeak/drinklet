# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ingredients', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=30)),
                ('ratings_sum', models.PositiveIntegerField()),
                ('total_ratings', models.PositiveIntegerField()),
                ('instructions', models.CharField(max_length=1000)),
            ],
        ),
        migrations.CreateModel(
            name='RecipeIngredients',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('quantity', models.PositiveSmallIntegerField()),
                ('ingredient', models.ForeignKey(to='ingredients.Ingredient')),
                ('recipe', models.ForeignKey(to='recipes.Recipe')),
            ],
        ),
    ]
