# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0009_auto_20141218_1807'),
    ]

    operations = [
        migrations.AddField(
            model_name='charactersheet',
            name='skillPoints',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
    ]
