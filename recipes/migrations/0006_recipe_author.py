# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def fill_authors(apps, schema_editor):
    UserProfile = apps.get_model('user', 'UserProfile')
    users = UserProfile.objects.all()

    for user in users:
        created_recipes = user.created_recipes.all()
        created_recipes.update(author=user)


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_auto_20151122_2103'),
        ('recipes', '0005_auto_20151122_2103'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='author',
            field=models.ForeignKey(default=0, to='user.UserProfile', related_name='created_recipe'),
            preserve_default=False,
        ),
        migrations.RunPython(fill_authors),
    ]
