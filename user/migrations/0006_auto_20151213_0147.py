# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-13 01:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0005_auto_20151209_1930'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipecomment',
            name='timestamp',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
