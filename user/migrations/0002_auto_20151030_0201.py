# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('ingredients', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipes', '0002_auto_20151030_0201'),
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserCreatedRecipes',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('recipe', models.ForeignKey(to='recipes.Recipe')),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('created_recipes', models.ManyToManyField(to='recipes.Recipe', through='user.UserCreatedRecipes', related_name='user_created_recipes')),
            ],
        ),
        migrations.AlterField(
            model_name='userfavorite',
            name='user',
            field=models.ForeignKey(to='user.UserProfile'),
        ),
        migrations.AlterField(
            model_name='useringredients',
            name='user',
            field=models.ForeignKey(to='user.UserProfile'),
        ),
        migrations.AlterField(
            model_name='userreciperating',
            name='user',
            field=models.ForeignKey(to='user.UserProfile'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='favorites',
            field=models.ManyToManyField(to='recipes.Recipe', through='user.UserFavorite', related_name='user_favorites'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='ingredients',
            field=models.ManyToManyField(to='ingredients.Ingredient', through='user.UserIngredients', related_name='user_ingredients'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='recipe_ratings',
            field=models.ManyToManyField(to='recipes.Recipe', through='user.UserRecipeRating', related_name='user_ratings'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='user',
            field=models.OneToOneField(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='usercreatedrecipes',
            name='user',
            field=models.ForeignKey(to='user.UserProfile'),
        ),
    ]
