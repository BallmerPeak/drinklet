# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0006_recipe_author'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='author',
            field=models.ForeignKey(to='user.UserProfile', related_name='created_recipes'),
        ),
    ]
