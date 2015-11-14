# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('statistics', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='walletbalanceentry',
            name='description',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='walletbalanceentry',
            name='wallet_division',
            field=models.IntegerField(null=True),
        ),
    ]
