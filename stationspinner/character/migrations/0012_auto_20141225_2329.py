# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0011_auto_20141225_2245'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='broken',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='notification',
            name='parsed_message',
            field=models.TextField(null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='notification',
            name='raw_message',
            field=models.TextField(null=True),
            preserve_default=True,
        ),
    ]
