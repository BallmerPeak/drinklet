# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_auto_20151030_0202'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userfavorite',
            name='recipe',
        ),
        migrations.RemoveField(
            model_name='userfavorite',
            name='user',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='favorites',
        ),
        migrations.DeleteModel(
            name='UserFavorite',
        ),
    ]
