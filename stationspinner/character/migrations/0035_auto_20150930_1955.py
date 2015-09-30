# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0034_auto_20150920_1132'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jumpclone',
            name='jumpCloneID',
            field=models.BigIntegerField(serialize=False, primary_key=True),
        ),
    ]
