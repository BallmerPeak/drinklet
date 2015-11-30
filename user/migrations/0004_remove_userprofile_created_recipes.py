# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_auto_20151122_2103'),
        ('recipes', '0006_recipe_author'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='created_recipes',
        ),
    ]
