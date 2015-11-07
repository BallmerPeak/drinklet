# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_auto_20151103_1316'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipeingredients',
            name='quantity',
            field=models.FloatField(),
        ),
    ]
