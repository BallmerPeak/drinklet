# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_auto_20151030_0201'),
        ('user', '0004_auto_20151031_1428'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='favorites',
            field=models.ManyToManyField(to='recipes.Recipe'),
        ),
    ]
