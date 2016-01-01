# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django_pgjson.fields


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0005_auto_20150919_2207'),
    ]

    operations = [
        migrations.AddField(
            model_name='apikey',
            name='characterIDs',
            field=django_pgjson.fields.JsonField(default=[], null=True),
        ),
        migrations.AlterField(
            model_name='apikey',
            name='characterID',
            field=models.BigIntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='apikey',
            name='corporationID',
            field=models.BigIntegerField(null=True, blank=True),
        ),
    ]
