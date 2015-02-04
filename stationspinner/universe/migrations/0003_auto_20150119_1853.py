# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('universe', '0002_evename'),
    ]

    operations = [
        migrations.AlterField(
            model_name='evename',
            name='name',
            field=models.CharField(max_length=255, null=True, db_index=True),
            preserve_default=True,
        ),
    ]
