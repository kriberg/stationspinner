# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import stationspinner.libs.fields


class Migration(migrations.Migration):

    dependencies = [
        ('universe', '0002_auto_20140927_1713'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alliance',
            name='memberCount',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='alliance',
            name='startDate',
            field=stationspinner.libs.fields.DateTimeField(null=True),
        ),
    ]
