# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-14 18:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0007_auto_20151130_1530'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='instructions_blob',
            field=models.CharField(max_length=4000),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='name',
            field=models.CharField(max_length=50, unique=True),
        ),
    ]
