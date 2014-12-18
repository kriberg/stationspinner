# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0003_auto_20141217_2116'),
    ]

    operations = [
        migrations.RenameField(
            model_name='jumpcloneimplant',
            old_name='jumpCloneID',
            new_name='jumpClone',
        ),
        migrations.AlterUniqueTogether(
            name='jumpcloneimplant',
            unique_together=set([('jumpClone', 'typeID')]),
        ),
    ]
