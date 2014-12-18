# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0004_auto_20141217_2127'),
    ]

    operations = [
        migrations.RenameField(
            model_name='jumpcloneimplant',
            old_name='jumpClone',
            new_name='jumpCloneID',
        ),
        migrations.AlterUniqueTogether(
            name='jumpcloneimplant',
            unique_together=set([('jumpCloneID', 'typeID')]),
        ),
    ]
