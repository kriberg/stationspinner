# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import stationspinner.libs.fields


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='apiupdate',
            name='cached_until',
            field=stationspinner.libs.fields.DateTimeField(null=True),
            preserve_default=True,
        ),
    ]
