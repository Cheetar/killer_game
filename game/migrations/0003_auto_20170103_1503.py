# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-03 14:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0002_auto_20170103_1502'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='death_note',
            field=models.CharField(blank=True, max_length=2000, null=True),
        ),
    ]
