# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('universe', '0004_auto_20140928_0326'),
    ]

    operations = [
        migrations.AddField(
            model_name='alliance',
            name='endDate',
            field=models.DateField(null=True),
            preserve_default=True,
        ),
    ]
