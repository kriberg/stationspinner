# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0006_auto_20160101_2113'),
    ]

    operations = [
        migrations.AddField(
            model_name='capsuler',
            name='owner_hash',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
