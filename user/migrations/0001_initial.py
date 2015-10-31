# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0001_initial'),
        ('auth', '0006_require_contenttypes_0002'),
        ('ingredients', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='RecipeComment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('comment_text', models.CharField(max_length=500)),
                ('recipe', models.ForeignKey(to='recipes.Recipe')),
            ],
        ),
        migrations.CreateModel(
            name='UserIngredients',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('quantity', models.PositiveIntegerField(default=0)),
                ('ingredient', models.ForeignKey(to='ingredients.Ingredient')),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL, primary_key=True, serialize=False)),
                ('created_recipes', models.ManyToManyField(related_name='user_created_recipes', to='recipes.Recipe')),
                ('favorites', models.ManyToManyField(related_name='user_favorites', to='recipes.Recipe')),
                ('ingredients', models.ManyToManyField(related_name='user_ingredients', to='ingredients.Ingredient', through='user.UserIngredients')),
            ],
        ),
        migrations.CreateModel(
            name='UserRecipeRating',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('rating', models.PositiveSmallIntegerField(default=0, validators=[django.core.validators.MaxValueValidator(5)])),
                ('recipe', models.ForeignKey(to='recipes.Recipe')),
                ('user', models.ForeignKey(to='user.UserProfile')),
            ],
        ),
        migrations.AddField(
            model_name='userprofile',
            name='recipe_ratings',
            field=models.ManyToManyField(related_name='user_ratings', to='recipes.Recipe', through='user.UserRecipeRating'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='user_recipe_comments',
            field=models.ManyToManyField(related_name='recipe_comments', to='recipes.Recipe', through='user.RecipeComment'),
        ),
        migrations.AddField(
            model_name='useringredients',
            name='user',
            field=models.ForeignKey(to='user.UserProfile'),
        ),
        migrations.AddField(
            model_name='recipecomment',
            name='user',
            field=models.ForeignKey(to='user.UserProfile'),
        ),
    ]
