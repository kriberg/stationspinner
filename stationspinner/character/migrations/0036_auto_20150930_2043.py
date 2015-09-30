# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0035_auto_20150930_1955'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jumpcloneimplant',
            name='jumpCloneID',
            field=models.BigIntegerField(),
        ),
    ]
