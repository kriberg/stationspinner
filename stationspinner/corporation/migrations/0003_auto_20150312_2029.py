# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('corporation', '0002_accountbalance_updated'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accountbalance',
            name='updated',
            field=models.DateTimeField(default=datetime.datetime(2015, 3, 12, 20, 29, 54, 410933, tzinfo=utc), auto_now=True),
            preserve_default=True,
        ),
    ]
