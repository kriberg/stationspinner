# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0006_auto_20141217_2139'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jumpcloneimplant',
            name='jumpCloneID',
            field=models.IntegerField(),
            preserve_default=True,
        ),
    ]
