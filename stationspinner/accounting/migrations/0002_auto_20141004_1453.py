# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='apikey',
            name='characterID',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='apikey',
            name='corporationID',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
    ]
