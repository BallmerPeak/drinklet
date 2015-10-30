# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_auto_20151102_0121'),
    ]

    operations = [
        migrations.RenameField(
            model_name='recipe',
            old_name='total_ratings',
            new_name='num_ratings',
        ),
    ]
