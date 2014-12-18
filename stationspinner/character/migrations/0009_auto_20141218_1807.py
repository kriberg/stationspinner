# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0008_jumpcloneimplant_owner'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jumpclone',
            name='locationID',
            field=models.BigIntegerField(),
            preserve_default=True,
        ),
    ]
