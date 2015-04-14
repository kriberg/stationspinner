# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('corporation', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='accountbalance',
            name='updated',
            field=models.DateTimeField(default=datetime.datetime(2015, 3, 12, 20, 17, 28, 699356, tzinfo=utc), auto_now=True),
            preserve_default=True,
        ),
    ]
