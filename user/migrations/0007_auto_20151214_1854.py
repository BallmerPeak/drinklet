# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-14 18:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0006_auto_20151213_0147'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipecomment',
            name='comment_text',
            field=models.CharField(max_length=1000),
        ),
    ]
