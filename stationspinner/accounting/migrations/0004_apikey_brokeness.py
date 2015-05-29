# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0003_auto_20150516_1908'),
    ]

    operations = [
        migrations.AddField(
            model_name='apikey',
            name='brokeness',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
    ]
