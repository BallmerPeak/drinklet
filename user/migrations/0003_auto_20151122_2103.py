# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_auto_20151103_1418'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useringredients',
            name='quantity',
            field=models.DecimalField(max_digits=8, default=0, decimal_places=2),
        ),
    ]
