# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corporation', '0012_auto_20150920_1828'),
    ]

    operations = [
        migrations.AddField(
            model_name='walletjournal',
            name='accountKey',
            field=models.IntegerField(null=True),
        ),
    ]
