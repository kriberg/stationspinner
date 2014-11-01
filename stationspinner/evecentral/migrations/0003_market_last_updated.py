# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('evecentral', '0002_auto_20141101_2338'),
    ]

    operations = [
        migrations.AddField(
            model_name='market',
            name='last_updated',
            field=models.DateTimeField(null=True),
            preserve_default=True,
        ),
    ]
