# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0005_userprofile_favorites'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useringredients',
            name='quantity',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='userreciperating',
            name='rating',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MaxValueValidator(5)], default=0),
        ),
    ]
