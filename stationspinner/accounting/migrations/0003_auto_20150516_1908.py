# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0002_apiupdate_cached_until'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apikey',
            name='characterID',
            field=models.IntegerField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='apikey',
            name='corporationID',
            field=models.IntegerField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
