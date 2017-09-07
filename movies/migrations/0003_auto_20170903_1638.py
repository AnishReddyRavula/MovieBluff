# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-09-03 11:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0002_auto_20170903_1108'),
    ]

    operations = [
        migrations.AlterField(
            model_name='watched',
            name='movie_rating',
            field=models.IntegerField(blank=True, choices=[(1, 'WORSE'), (2, 'BAD'), (3, 'AVERAGE'), (4, 'GOOD'), (5, 'EXCELLENT')], null=True),
        ),
    ]
